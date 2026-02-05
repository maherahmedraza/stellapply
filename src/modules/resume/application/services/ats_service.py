import logging
from typing import List, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from src.core.ai.gemini_client import GeminiClient
from src.modules.persona.domain.services import PersonaService
from src.modules.resume.application.services.skill_matcher import (
    SkillMatcher,
    MatchType,
)

logger = logging.getLogger(__name__)


class ATSOptimizationResult(BaseModel):
    """Result of truth-grounded ATS optimization"""

    matched_skills: list[dict[str, Any]] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    partial_matches: list[dict[str, Any]] = Field(default_factory=list)
    optimization_suggestions: list[str] = Field(default_factory=list)
    match_score: float = Field(ge=0.0, le=1.0, default=0.0)
    truthfulness_note: str = ""


class TruthfulATSOptimizer:
    """
    ATS optimization that maintains truthfulness.
    Only aligns EXISTING skills with job requirements.
    """

    def __init__(
        self,
        gemini_client: GeminiClient,
        persona_service: PersonaService,
        skill_matcher: Optional[SkillMatcher] = None,
    ):
        self.gemini = gemini_client
        self.persona_service = persona_service
        self.skill_matcher = skill_matcher or SkillMatcher()

    async def optimize_for_ats(
        self, resume_id: UUID, job_description: str, user_id: UUID
    ) -> ATSOptimizationResult:
        """
        Optimize resume for ATS without fabricating.
        """
        # Validate inputs
        if not job_description or not job_description.strip():
            return ATSOptimizationResult(
                truthfulness_note="Job description is required for ATS optimization."
            )

        # Load user's verified skills
        try:
            persona = await self.persona_service.get_persona_by_user_id(user_id)
        except Exception as e:
            logger.error(f"Failed to load persona for user {user_id}: {e}")
            return ATSOptimizationResult(
                optimization_suggestions=[
                    "Unable to load your profile. Please try again."
                ],
                truthfulness_note="Error loading profile data.",
            )

        if not persona:
            return ATSOptimizationResult(
                optimization_suggestions=["Please complete your persona first."],
                truthfulness_note="No profile data found to optimize against.",
            )

        if not persona.skills:
            return ATSOptimizationResult(
                optimization_suggestions=[
                    "Add skills to your profile to enable ATS optimization."
                ],
                truthfulness_note="No skills found in your profile.",
            )

        # Build skill lookup
        user_skills = {s.name.lower(): s for s in persona.skills}

        # Extract JD requirements
        try:
            jd_requirements = await self._extract_jd_requirements(job_description)
        except Exception as e:
            logger.error(f"Failed to extract JD requirements: {e}")
            jd_requirements = self._fallback_extract_requirements(job_description)

        if not jd_requirements:
            return ATSOptimizationResult(
                optimization_suggestions=[
                    "Could not extract requirements from job description."
                ],
                truthfulness_note="Unable to parse job requirements.",
            )

        # Match skills
        matched_skills = []
        partial_matches = []
        missing_skills = []

        for req_skill in jd_requirements:
            match = self.skill_matcher.match(req_skill, user_skills)

            if match:
                match_dict = {
                    "required_skill": match.required_skill,
                    "your_skill": match.matched_skill,
                    "match_type": match.match_type.value,
                    "confidence": match.confidence,
                }
                if match.proficiency:
                    match_dict["proficiency"] = match.proficiency

                if match.match_type in (MatchType.EXACT, MatchType.SYNONYM):
                    matched_skills.append(match_dict)
                else:
                    partial_matches.append(match_dict)
            else:
                missing_skills.append(req_skill)

        # Calculate match score
        total_required = len(jd_requirements)
        full_matches = len(matched_skills)
        partial_count = len(partial_matches)

        match_score = (
            (full_matches + (partial_count * 0.5)) / total_required
            if total_required > 0
            else 0
        )

        # Generate optimization suggestions
        suggestions = self._generate_suggestions(
            matched_skills, partial_matches, missing_skills
        )

        return ATSOptimizationResult(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            partial_matches=partial_matches,
            optimization_suggestions=suggestions,
            match_score=round(match_score, 2),
            truthfulness_note=(
                f"Matched {full_matches}/{total_required} required skills. "
                f"Only your existing skills were used. "
                f"Missing skills are listed for your awareness—consider learning them if interested."
            ),
        )

    async def _extract_jd_requirements(self, job_description: str) -> list[str]:
        """Extract key skills and requirements from a job description using Gemini"""
        prompt = f"""
        Extract technical skills, tools, frameworks, and certifications from this job description.
        Return ONLY a JSON array of strings, no duplicates, lowercase.
        Focus on concrete, verifiable skills (e.g., "python", "aws", "kubernetes").
        Exclude soft skills and generic requirements.
        
        JOB DESCRIPTION:
        {job_description[:3000]}
        
        Example output: ["python", "aws", "kubernetes", "postgresql"]
        """

        try:
            response = await self.gemini.generate_structured(
                prompt=prompt, schema=list[str]
            )
            seen = set()
            result = []
            for skill in response:
                normalized = skill.lower().strip()
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    result.append(normalized)
            return result
        except Exception as e:
            logger.warning(f"Gemini extraction failed, using fallback: {e}")
            return self._fallback_extract_requirements(job_description)

    def _fallback_extract_requirements(self, job_description: str) -> list[str]:
        """Fallback extraction using keyword matching"""
        import re

        tech_patterns = [
            r"\b(python|java|javascript|typescript|golang?|rust|c\+\+|c#|ruby|php|swift|kotlin)\b",
            r"\b(react|angular|vue|next\.?js|node\.?js|express|django|flask|spring|rails)\b",
            r"\b(aws|azure|gcp|kubernetes|docker|terraform|jenkins|github actions)\b",
            r"\b(postgresql|mysql|mongodb|redis|elasticsearch|kafka)\b",
            r"\b(machine learning|deep learning|nlp|computer vision|data science)\b",
            r"\b(rest|graphql|grpc|microservices|api)\b",
            r"\b(git|linux|unix|bash|shell)\b",
            r"\b(agile|scrum|jira|confluence)\b",
        ]
        text_lower = job_description.lower()
        found = set()
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_lower)
            found.update(matches)
        return list(found)

    def _generate_suggestions(
        self, matched: list[Dict], partial: list[Dict], missing: list[str]
    ) -> list[str]:
        """Generate actionable optimization suggestions"""
        suggestions = []
        if matched:
            top_matches = sorted(
                matched, key=lambda x: x.get("proficiency", 0), reverse=True
            )[:5]
            skill_names = [m["your_skill"] for m in top_matches]
            suggestions.append(
                f"Highlight these matching skills prominently: {', '.join(skill_names)}"
            )
        if partial:
            for p in partial[:3]:
                suggestions.append(
                    f"Your '{p['your_skill']}' partially matches required '{p['required_skill']}' - "
                    f"ensure your resume uses exact terminology if applicable"
                )
        if missing:
            if len(missing) <= 3:
                suggestions.append(
                    f"Skills gap: {', '.join(missing)} - consider acquiring these"
                )
            else:
                suggestions.append(
                    f"Skills gap: {', '.join(missing[:3])} and {len(missing) - 3} more - "
                    f"review if this role is a good fit"
                )
        if not matched:
            suggestions.append(
                "Low skill match detected. Consider roles more aligned with your current skillset, "
                "or invest in learning the required skills."
            )
        return suggestions
