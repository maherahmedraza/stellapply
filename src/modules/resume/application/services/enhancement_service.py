from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from uuid import UUID
import logging
import re

from pydantic import BaseModel, Field

from src.core.ai.gemini_client import GeminiClient
from src.modules.persona.domain.models import Persona, Experience
from src.modules.persona.domain.repository import PersonaRepository
from src.modules.resume.infrastructure.rules.engine import (
    EnhancementRulesEngine,
    ValidationResult,
)
from src.modules.resume.infrastructure.rules.base import RuleSeverity
from src.modules.resume.infrastructure.cache.enhancement_cache import EnhancementCache

logger = logging.getLogger(__name__)

# ============================================================================
# VALUE OBJECTS
# ============================================================================


class EnhancementType(str, Enum):
    REPHRASE = "rephrase"
    QUANTIFY = "quantify"
    STRUCTURE = "structure"
    KEYWORD = "keyword"
    ACTION_VERB = "action_verb"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"  # Fully grounded in persona
    PLAUSIBLE = "plausible"  # Reasonable inference
    NEEDS_CONFIRMATION = "needs_confirmation"  # User must confirm
    REJECTED = "rejected"  # Cannot be used


# ============================================================================
# DATA TRANSFER OBJECTS
# ============================================================================


class EnhancementRequest(BaseModel):
    """Request for enhancement"""

    content: str
    content_type: str  # "bullet_point", "summary", "description"
    target_keywords: Optional[list[str]] = None
    context: Optional[dict[str, Any]] = None


class EnhancementSuggestion(BaseModel):
    """A single enhancement suggestion with full metadata"""

    original_text: str
    enhanced_text: str
    enhancement_type: EnhancementType

    # Verification
    verification_status: VerificationStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    defensibility_score: float = Field(ge=0.0, le=1.0)

    # Source tracking
    source_persona_fields: list[str] = Field(default_factory=list)
    verification_notes: str = ""

    # Changes made
    changes_made: list[str] = Field(default_factory=list)

    # Interview preparation
    interview_talking_points: list[str] = Field(default_factory=list)

    # Confirmation handling
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    placeholders: list[str] = Field(default_factory=list)


class EnhancementResponse(BaseModel):
    """Response containing enhancement suggestions"""

    success: bool
    suggestions: list[EnhancementSuggestion] = Field(default_factory=list)
    validation_result: Optional[dict[str, Any]] = None
    error: Optional[str] = None


# ============================================================================
# PERSONA CONTEXT BUILDER
# ============================================================================


@dataclass
class PersonaContext:
    """
    Extracted context from Persona for verification.
    """

    verified_skills: set[str] = field(default_factory=set)
    verified_tools: set[str] = field(default_factory=set)
    verified_companies: set[str] = field(default_factory=set)
    verified_job_titles: set[str] = field(default_factory=set)
    verified_industries: set[str] = field(default_factory=set)
    verified_achievements: list[dict[str, Any]] = field(default_factory=list)
    verified_metrics: list[str] = field(default_factory=list)
    verified_responsibilities: list[dict[str, Any]] = field(default_factory=list)
    years_of_experience: dict[str, float] = field(default_factory=dict)
    education: list[dict[str, Any]] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    projects: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verified_skills": self.verified_skills,
            "verified_tools": self.verified_tools,
            "verified_companies": self.verified_companies,
            "verified_job_titles": self.verified_job_titles,
            "verified_industries": self.verified_industries,
            "verified_achievements": self.verified_achievements,
            "verified_metrics": self.verified_metrics,
            "verified_responsibilities": self.verified_responsibilities,
            "years_of_experience": self.years_of_experience,
            "education": self.education,
            "certifications": self.certifications,
            "projects": self.projects,
        }

    @classmethod
    def from_persona(cls, persona: Persona) -> "PersonaContext":
        context = cls()

        # Extract skills
        for skill in persona.skills:
            name_lower = skill.name.lower()
            context.verified_skills.add(name_lower)
            if hasattr(skill, "category") and skill.category == "TOOL":
                context.verified_tools.add(name_lower)

        # Extract from experiences
        for exp in persona.experiences:
            context.verified_companies.add(exp.company_name.lower())
            context.verified_job_titles.add(exp.job_title.lower())

            duration = cls._calculate_duration(exp)
            for skill_name in exp.skills_used or []:
                skill_lower = skill_name.lower()
                context.years_of_experience[skill_lower] = (
                    context.years_of_experience.get(skill_lower, 0) + duration
                )

            for achievement in exp.achievements or []:
                metrics = cls._extract_metrics(achievement)
                context.verified_achievements.append(
                    {
                        "text": achievement,
                        "company": exp.company_name,
                        "role": exp.job_title,
                        "metrics": metrics,
                    }
                )
                context.verified_metrics.extend(metrics)

            desc = exp.description_active or exp.description_original
            if desc:
                context.verified_responsibilities.append(
                    {
                        "description": desc,
                        "company": exp.company_name,
                        "role": exp.job_title,
                    }
                )

        # Extract education
        for edu in persona.educations or []:
            context.education.append(
                {
                    "degree": str(edu.degree_type),
                    "field": edu.field_of_study,
                    "institution": edu.institution_name,
                }
            )

        # Extract certifications
        for cert in persona.certifications or []:
            context.certifications.append(cert.name.lower())

        # Extract projects
        for project in persona.projects or []:
            context.projects.append(
                {
                    "name": project.name,
                    "description": project.description,
                    "tech": project.technologies,
                }
            )
            for tech in project.technologies or []:
                context.verified_tools.add(tech.lower())

        return context

    @staticmethod
    def _calculate_duration(experience: Experience) -> float:
        if not experience.start_date:
            return 0.0
        end = experience.end_date or datetime.now(timezone.utc).date()
        start = experience.start_date
        days = (end - start).days
        return max(0.0, days / 365.25)

    @staticmethod
    def _extract_metrics(text: str) -> list[str]:
        patterns = [
            r"\d+%",
            r"\$[\d,]+(?:\.\d{2})?[KMB]?",
            r"\d+x",
            r"\d+\s*(?:users|customers|clients|employees)",
        ]
        metrics = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.extend(matches)
        return metrics


# ============================================================================
# MAIN SERVICE
# ============================================================================


class EnhancementService:
    """
    Unified service for truth-grounded CV enhancement.
    """

    ENHANCEMENT_PROMPT = """
You are a professional resume writer with a STRICT ethical code.
Your job is to improve resume content while NEVER adding false information.

## ABSOLUTE RULES:
1. NEVER add skills not in the VERIFIED SKILLS list
2. NEVER invent metrics - use PLACEHOLDERS like [X%] or [N users] for new numbers
3. NEVER exaggerate experience levels or responsibilities
4. NEVER fabricate achievements or companies
5. If you cannot improve truthfully, return the original unchanged

## WHAT YOU CAN DO:
1. Use stronger action verbs for REAL activities
2. Restructure for clarity and impact
3. Add keywords from verified skills (if relevant)
4. Suggest metric placeholders the user should fill in
5. Make content more concise

## VERIFIED INFORMATION (Source of Truth):
Skills: {skills}
Tools: {tools}
Companies: {companies}
Job Titles: {titles}
Certifications: {certifications}
Experience Summary: {experience_summary}

## TARGET KEYWORDS (only use if user has the skill):
{target_keywords}

## CONTENT TO ENHANCE:
Type: {content_type}
Original: "{original_content}"

## RESPOND WITH JSON:
{{
    "enhancements": [
        {{
            "enhanced_text": "improved version",
            "enhancement_type": "rephrase|quantify|structure|keyword|action_verb",
            "confidence": 0.0-1.0,
            "skills_mentioned": ["skill1", "skill2"],
            "changes_made": ["change 1", "change 2"],
            "has_placeholders": true/false,
            "needs_confirmation": true/false,
            "confirmation_question": "question if needs_confirmation"
        }}
    ]
}}
"""

    def __init__(
        self,
        gemini_client: GeminiClient,
        persona_repository: PersonaRepository,
        rules_engine: Optional[EnhancementRulesEngine] = None,
        cache: Optional[EnhancementCache] = None,
        verification_threshold: float = 0.8,
    ):
        self.gemini = gemini_client
        self.persona_repo = persona_repository
        self.rules_engine = rules_engine or EnhancementRulesEngine()
        self.cache = cache
        self.verification_threshold = verification_threshold

    async def enhance(
        self, user_id: UUID, request: EnhancementRequest
    ) -> EnhancementResponse:
        """
        Main entry point for enhancement requests.
        """
        try:
            persona = await self.persona_repo.get_by_user_id(user_id)
        except Exception as e:
            logger.error(f"Failed to load persona for user {user_id}: {e}")
            return EnhancementResponse(
                success=False, error="Failed to load your profile. Please try again."
            )

        if not persona:
            return EnhancementResponse(
                success=False,
                error="Please complete your profile before using AI enhancement.",
            )

        context = PersonaContext.from_persona(persona)

        cache_key = self._build_cache_key(user_id, request)
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        try:
            raw_enhancements = await self._generate_enhancements(
                request=request, context=context
            )
        except Exception as e:
            logger.error(f"AI enhancement generation failed: {e}")
            return EnhancementResponse(
                success=False,
                error="AI enhancement temporarily unavailable. Please try again.",
            )

        verified_suggestions = []
        for raw in raw_enhancements:
            suggestion = await self._verify_and_build_suggestion(
                raw_enhancement=raw,
                original_text=request.content,
                persona=persona,
                context=context,
            )

            if suggestion.verification_status != VerificationStatus.REJECTED:
                verified_suggestions.append(suggestion)

        response = EnhancementResponse(success=True, suggestions=verified_suggestions)

        if self.cache and verified_suggestions:
            await self.cache.set(cache_key, response, ttl=3600)

        return response

    async def _generate_enhancements(
        self, request: EnhancementRequest, context: PersonaContext
    ) -> list[dict[str, Any]]:
        prompt = self.ENHANCEMENT_PROMPT.format(
            skills=list(context.verified_skills),
            tools=list(context.verified_tools),
            companies=list(context.verified_companies),
            titles=list(context.verified_job_titles),
            certifications=context.certifications,
            experience_summary=context.years_of_experience,
            target_keywords=request.target_keywords or "None specified",
            content_type=request.content_type,
            original_content=request.content,
        )

        class EnhancementItem(BaseModel):
            enhanced_text: str
            enhancement_type: str
            confidence: float
            skills_mentioned: list[str] = []
            changes_made: list[str] = []
            has_placeholders: bool = False
            needs_confirmation: bool = False
            confirmation_question: Optional[str] = None

        class EnhancementList(BaseModel):
            enhancements: list[EnhancementItem]

        response = await self.gemini.generate_structured(
            prompt=prompt, schema=EnhancementList
        )

        return [e.model_dump() for e in response.enhancements]

    async def _verify_and_build_suggestion(
        self,
        raw_enhancement: dict[str, Any],
        original_text: str,
        persona: Persona,
        context: PersonaContext,
    ) -> EnhancementSuggestion:
        enhanced_text = raw_enhancement["enhanced_text"]

        validation = self.rules_engine.validate_enhancement(
            original=original_text, enhanced=enhanced_text, context=context.to_dict()
        )

        if validation.blocking_violations:
            status = VerificationStatus.REJECTED
            notes = f"Rejected: {', '.join(v.description for v in validation.blocking_violations)}"
            defensibility = 0.0
        elif validation.requires_confirmation:
            status = VerificationStatus.NEEDS_CONFIRMATION
            notes = f"Needs confirmation: {', '.join(v.description for v in validation.warnings)}"
            defensibility = 0.7
        else:
            status = VerificationStatus.VERIFIED
            notes = "All claims verified against your profile"
            defensibility = 0.95

        defensibility = self._calculate_defensibility(
            enhanced_text=enhanced_text, context=context, base_score=defensibility
        )

        talking_points = self._generate_talking_points(
            enhanced_text=enhanced_text, persona=persona, context=context
        )

        placeholders = re.findall(r"\[.*?\]", enhanced_text)

        return EnhancementSuggestion(
            original_text=original_text,
            enhanced_text=enhanced_text,
            enhancement_type=EnhancementType(
                raw_enhancement.get("enhancement_type", "rephrase")
            ),
            verification_status=status,
            confidence_score=raw_enhancement.get("confidence", 0.8),
            defensibility_score=defensibility,
            source_persona_fields=raw_enhancement.get("skills_mentioned", []),
            verification_notes=notes,
            changes_made=raw_enhancement.get("changes_made", []),
            interview_talking_points=talking_points,
            requires_confirmation=status == VerificationStatus.NEEDS_CONFIRMATION,
            confirmation_prompt=raw_enhancement.get("confirmation_question"),
            placeholders=placeholders,
        )

    def _calculate_defensibility(
        self, enhanced_text: str, context: PersonaContext, base_score: float
    ) -> float:
        score = base_score
        text_lower = enhanced_text.lower()

        metrics = PersonaContext._extract_metrics(enhanced_text)
        for metric in metrics:
            if metric not in context.verified_metrics:
                score -= 0.1

        superlatives = ["best", "top", "leading", "premier", "only", "first"]
        for sup in superlatives:
            if sup in text_lower:
                score -= 0.05

        for company in context.verified_companies:
            if company in text_lower:
                score += 0.05
                break

        return max(0.0, min(1.0, score))

    def _generate_talking_points(
        self, enhanced_text: str, persona: Persona, context: PersonaContext
    ) -> list[str]:
        points = []
        for exp in persona.experiences:
            for ach in exp.achievements or []:
                if self._text_similarity(ach, enhanced_text) > 0.3:
                    points.append(f"Reference your work at {exp.company_name}: {ach}")

        for skill_name in context.verified_skills:
            if skill_name in enhanced_text.lower():
                years = context.years_of_experience.get(skill_name, 0)
                if years > 0:
                    points.append(
                        f"Mention {years:.1f} years of {skill_name} experience"
                    )

        return points[:3]

    @staticmethod
    def _text_similarity(text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)

    def _build_cache_key(self, user_id: UUID, request: EnhancementRequest) -> str:
        import hashlib

        content_hash = hashlib.md5(request.content.encode()).hexdigest()[:8]
        return f"enhance:{user_id}:{request.content_type}:{content_hash}"

    async def confirm_placeholders(
        self, enhanced_text: str, placeholder_values: dict[str, str]
    ) -> str:
        """
        Replace placeholders [X%], [N users] etc with actual user-provided values.
        """
        final_text = enhanced_text
        for placeholder, value in placeholder_values.items():
            if value:
                # Replace exact placeholder match
                final_text = final_text.replace(placeholder, value)

        return final_text
