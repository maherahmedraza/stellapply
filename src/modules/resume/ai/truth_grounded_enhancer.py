"""
Truth-Grounded CV Enhancement System
====================================
All enhancements are verified against the user's Persona (source of truth)
before being suggested or applied.
"""

import re
import logging
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any, Optional, Set

from src.core.ai.gemini_client import GeminiClient
from src.modules.persona.domain.models import Persona, Experience, Skill
from src.modules.persona.domain.repository import PersonaRepository
from src.modules.resume.domain.truth_grounded_schemas import (
    EnhancementType,
    VerificationStatus,
    EnhancementSuggestionSchema,
    EnhancementResponse,
)
from src.modules.resume.ai.enhancement_rules import (
    EnhancementRulesEngine,
    RuleViolationType,
)
from src.modules.resume.ai.prompts import TRUTH_GROUNDED_ENHANCEMENT_PROMPT

logger = logging.getLogger(__name__)


class TruthGroundedEnhancer:
    """
    AI-powered CV enhancement that is strictly grounded in the user's
    verified Persona data. Never invents or fabricates information.
    """

    METRIC_PATTERNS = [
        r"\d+%",  # Percentages
        r"\$[\d,]+",  # Dollar amounts
        r"\d+x",  # Multipliers
        r"\d+ (users|customers|clients)",  # User counts
        r"\d+ (team|people|engineers)",  # Team sizes
    ]

    def __init__(
        self,
        gemini_client: GeminiClient,
        persona_repository: PersonaRepository,
        verification_threshold: float = 0.8,
    ):
        self.gemini = gemini_client
        self.persona_repo = persona_repository
        self.verification_threshold = verification_threshold
        self.rules_engine = EnhancementRulesEngine()

    async def enhance_with_truth_verification(
        self,
        user_id: UUID,
        original_content: str,
        content_type: str,  # "bullet_point", "summary", "description"
        target_job_keywords: Optional[List[str]] = None,
    ) -> List[EnhancementSuggestionSchema]:
        """
        Generate enhancements that are strictly grounded in the user's Persona.
        """

        # Step 1: Load Persona as source of truth
        persona = await self.persona_repo.get_by_user_id(user_id)
        if not persona:
            logger.error(f"Persona not found for user {user_id}")
            return []

        # Step 2: Build verification context
        verification_context = self._build_verification_context(persona)

        # Step 3: Generate enhancements with strict grounding prompt
        raw_enhancements = await self._generate_grounded_enhancements(
            original_content=original_content,
            content_type=content_type,
            persona_context=verification_context,
            target_keywords=target_job_keywords,
        )

        # Step 4: Verify each enhancement
        verified_suggestions = []
        for enhancement in raw_enhancements:
            verified = await self._verify_enhancement(
                enhancement=enhancement,
                original_text=original_content,
                persona=persona,
                verification_context=verification_context,
            )

            # Step 5: Only include suggestions that aren't blocked
            if verified.verification_status != VerificationStatus.REJECTED:
                verified_suggestions.append(verified)

        return verified_suggestions

    def _build_verification_context(self, persona: Persona) -> Dict[str, Any]:
        """
        Build a comprehensive verification context from the Persona.
        """
        context = {
            "verified_skills": set(),
            "verified_tools": set(),
            "verified_industries": set(),
            "verified_job_titles": set(),
            "verified_companies": set(),
            "verified_achievements": [],
            "verified_metrics": [],
            "verified_responsibilities": [],
            "years_of_experience": {},
            "education": [],
            "certifications": [],
            "projects": [],
        }

        # Extract from skills
        for skill in persona.skills:
            name_lower = skill.name.lower()
            context["verified_skills"].add(name_lower)
            if skill.category.value == "TOOL":
                context["verified_tools"].add(name_lower)

        # Extract from experiences
        for exp in persona.experiences:
            context["verified_companies"].add(exp.company_name.lower())
            context["verified_job_titles"].add(exp.job_title.lower())

            # Duration calculation
            duration_years = self._calculate_experience_duration(exp)
            for skill_name in exp.skills_used:
                skill_lower = skill_name.lower()
                context["years_of_experience"][skill_lower] = (
                    context["years_of_experience"].get(skill_lower, 0) + duration_years
                )

            # Achievements and metrics
            for achievement in exp.achievements:
                metrics = self._extract_metrics(achievement)
                context["verified_achievements"].append(
                    {
                        "text": achievement,
                        "company": exp.company_name,
                        "role": exp.job_title,
                        "metrics": metrics,
                    }
                )
                context["verified_metrics"].extend(metrics)

            # Responsibilities
            desc = exp.description_active or exp.description_original
            if desc:
                context["verified_responsibilities"].append(
                    {
                        "description": desc,
                        "company": exp.company_name,
                        "role": exp.job_title,
                    }
                )

        # Extract from education
        for edu in persona.educations:
            context["education"].append(
                {
                    "degree": edu.degree_type.value,
                    "field": edu.field_of_study,
                    "institution": edu.institution_name,
                }
            )

        # Extract certifications
        for cert in persona.certifications:
            context["certifications"].append(cert.name.lower())

        # Extract projects
        for project in persona.projects:
            context["projects"].append(
                {
                    "name": project.name,
                    "description": project.description,
                    "tech": project.technologies,
                }
            )
            for tech in project.technologies:
                context["verified_tools"].add(tech.lower())

        return context

    async def _generate_grounded_enhancements(
        self,
        original_content: str,
        content_type: str,
        persona_context: Dict[str, Any],
        target_keywords: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate enhancements using Gemini with strict grounding instructions.
        """

        prompt = TRUTH_GROUNDED_ENHANCEMENT_PROMPT.format(
            skills=list(persona_context["verified_skills"]),
            tools=list(persona_context["verified_tools"]),
            companies=list(persona_context["verified_companies"]),
            titles=list(persona_context["verified_job_titles"]),
            certifications=persona_context["certifications"],
            experience_summary=persona_context["years_of_experience"],
            target_keywords=target_keywords or "None specified",
            content_type=content_type,
            original_content=original_content,
        )

        try:
            response = await self.gemini.generate_structured(
                prompt=prompt, schema=EnhancementResponse
            )
            return [e.model_dump() for e in response.enhancements]
        except Exception as e:
            logger.error(f"Error generating grounded enhancements: {str(e)}")
            return []

    async def _verify_enhancement(
        self,
        enhancement: Dict[str, Any],
        original_text: str,
        persona: Persona,
        verification_context: Dict[str, Any],
    ) -> EnhancementSuggestionSchema:
        """
        Verify that an enhancement is truthful and grounded in the Persona.
        """
        enhanced_text = enhancement["enhanced_text"]

        # Run rules engine validation
        validation_result = self.rules_engine.validate_enhancement(
            original_text, enhanced_text, verification_context
        )

        status = VerificationStatus.VERIFIED
        verification_notes = "All claims verified against Persona"
        requires_confirmation = False
        defensibility = 1.0

        if validation_result["blocking_violations"]:
            status = VerificationStatus.REJECTED
            verification_notes = f"Rejected due to: {', '.join([v['description'] for v in validation_result['blocking_violations']])}"
            defensibility = 0.0
        elif validation_result["requires_confirmation"]:
            status = VerificationStatus.NEEDS_CONFIRMATION
            verification_notes = f"Needs confirmation for: {', '.join([v['description'] for v in validation_result['warnings']])}"
            requires_confirmation = True
            defensibility = 0.7

        # Calculate final defensibility
        defensibility = self._calculate_defensibility(
            enhanced_text, verification_context, defensibility
        )

        # Generate talking points
        talking_points = self._generate_interview_talking_points(
            enhanced_text, persona, verification_context
        )

        return EnhancementSuggestionSchema(
            original_text=original_text,
            enhanced_text=enhanced_text,
            enhancement_type=EnhancementType(enhancement["enhancement_type"]),
            verification_status=status,
            confidence_score=enhancement.get("confidence", 0.9),
            source_persona_fields=list(set(enhancement.get("skills_mentioned", []))),
            verification_notes=verification_notes,
            changes_made=enhancement.get("changes_made", []),
            defensibility_score=defensibility,
            interview_talking_points=talking_points,
            requires_confirmation=requires_confirmation,
            confirmation_prompt=enhancement.get("confirmation_question"),
        )

    def _calculate_defensibility(
        self,
        enhanced_text: str,
        verification_context: Dict[str, Any],
        base_score: float,
    ) -> float:
        """
        Calculate how defensible this enhancement is in an interview.
        """
        score = base_score
        text_lower = enhanced_text.lower()

        # Deduct for unverified metrics
        metrics = self._extract_metrics(enhanced_text)
        verified_metrics = verification_context.get("verified_metrics", [])

        for metric in metrics:
            if metric not in verified_metrics:
                score -= 0.1

        # Deduct for superlatives
        superlatives = ["best", "top", "leading", "premier", "only", "first"]
        for sup in superlatives:
            if sup in text_lower:
                score -= 0.1

        # Boost for referencing verified entities
        for company in verification_context.get("verified_companies", []):
            if company.lower() in text_lower:
                score += 0.05
                break

        return max(0.0, min(1.0, score))

    def _generate_interview_talking_points(
        self, enhanced_text: str, persona: Persona, verification_context: Dict[str, Any]
    ) -> List[str]:
        """
        Generate talking points for interview preparation.
        """
        talking_points = []

        # Reference existing achievements
        for exp in persona.experiences:
            for ach in exp.achievements:
                if self._text_similarity(ach, enhanced_text) > 0.3:
                    talking_points.append(
                        f"Refer to your work at {exp.company_name}: {ach}"
                    )

        # Refer to specific skills
        for skill_name in verification_context["verified_skills"]:
            if skill_name in enhanced_text.lower():
                years = verification_context["years_of_experience"].get(skill_name, 0)
                if years > 0:
                    talking_points.append(
                        f"Mention {years:.1f} years of experience with {skill_name}"
                    )

        return talking_points[:3]  # Return top 3 points

    def _extract_metrics(self, text: str) -> List[str]:
        """Extract numeric metrics from text."""
        metrics = []
        for pattern in self.METRIC_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.extend([m[0] if isinstance(m, tuple) else m for m in matches])
        return metrics

    @staticmethod
    def _calculate_experience_duration(experience: Experience) -> float:
        """Calculate years of experience from an Experience object."""
        if not experience.start_date:
            return 0.0

        end = experience.end_date or datetime.now().date()
        start = experience.start_date

        days = (end - start).days
        return max(0.0, days / 365.25)

    @staticmethod
    def _text_similarity(text1: str, text2: str) -> float:
        """Simple word overlap similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)
