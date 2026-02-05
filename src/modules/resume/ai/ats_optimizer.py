from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel
from src.modules.resume.domain.models import Resume
from src.modules.persona.domain.services import PersonaService
from src.core.ai.gemini_client import GeminiClient


class ATSOptimizationResult(BaseModel):
    """Result of truth-grounded ATS optimization"""

    matched_skills: List[Dict[str, Any]]
    missing_skills: List[str]
    optimization_suggestions: List[str]
    truthfulness_note: str


class TruthfulATSOptimizer:
    """
    ATS optimization that maintains truthfulness.
    Only aligns EXISTING skills with job requirements.
    """

    def __init__(self, gemini_client: GeminiClient, persona_service: PersonaService):
        self.gemini = gemini_client
        self.persona_service = persona_service

    async def optimize_for_ats(
        self, resume: Resume, job_description: str, user_id: UUID
    ) -> ATSOptimizationResult:
        """
        Optimize resume for ATS without fabricating.
        """

        # Load user's verified skills
        persona = await self.persona_service.get_persona_by_user_id(user_id)
        if not persona:
            return ATSOptimizationResult(
                matched_skills=[],
                missing_skills=[],
                optimization_suggestions=["Please complete your persona first."],
                truthfulness_note="No personal data found to optimize against.",
            )

        user_skills = {s.name.lower(): s for s in persona.skills}

        # Extract JD requirements
        jd_requirements = await self._extract_jd_requirements(job_description)

        # Find matches (TRUTHFUL - only skills user has)
        matched_skills = []
        missing_skills = []

        for req_skill in jd_requirements:
            req_skill_lower = req_skill.lower()
            # Check exact match
            if req_skill_lower in user_skills:
                matched_skills.append(
                    {
                        "skill": req_skill,
                        "user_skill": user_skills[req_skill_lower].name,
                        "proficiency": user_skills[
                            req_skill_lower
                        ].proficiency_level.value
                        if hasattr(
                            user_skills[req_skill_lower].proficiency_level, "value"
                        )
                        else user_skills[req_skill_lower].proficiency_level,
                    }
                )
            # Check semantic similarity (e.g., "React" matches "React.js")
            elif similar := self._find_similar_skill(req_skill, user_skills):
                matched_skills.append(
                    {
                        "skill": req_skill,
                        "user_skill": similar,
                        "match_type": "semantic",
                    }
                )
            else:
                # User doesn't have this skill - DON'T ADD IT
                missing_skills.append(req_skill)

        return ATSOptimizationResult(
            matched_skills=matched_skills,
            missing_skills=missing_skills,  # Inform user, don't fabricate
            optimization_suggestions=[
                f"Move '{m['user_skill']}' higher in skills section"
                for m in matched_skills[:5]
            ],
            truthfulness_note="Only your existing skills were used. Missing skills are listed for your awareness - consider learning them if interested.",
        )

    async def _extract_jd_requirements(self, job_description: str) -> List[str]:
        """Extract key skills and requirements from a job description using Gemini"""
        prompt = f"""
        Extract a list of technical skills, tools, and certifications required in this job description.
        Return ONLY a JSON list of strings.
        
        JOB DESCRIPTION:
        {job_description}
        """
        try:
            response = await self.gemini.generate_structured(
                prompt=prompt, schema=List[str]
            )
            return response
        except Exception:
            # Fallback to simple extraction if LLM fails
            return []

    def _find_similar_skill(
        self, req_skill: str, user_skills: Dict[str, Any]
    ) -> Optional[str]:
        """Simple fuzzy match for similar skills"""
        req_lower = req_skill.lower()
        for user_skill_name in user_skills.keys():
            if req_lower in user_skill_name or user_skill_name in req_lower:
                return user_skills[user_skill_name].name
        return None
