from typing import Any
from uuid import UUID

from src.modules.persona.domain.models import Experience, Persona, Skill
from src.modules.persona.domain.repository import PersonaRepository
from src.modules.resume.domain.models import Resume
from src.modules.resume.domain.repository import ResumeRepository
from src.modules.resume.domain.schemas import (
    RenderedEducation,
    RenderedExperience,
    RenderedHeader,
    RenderedResume,
    RenderedSkill,
    ResumeUpdate,
)


class ResumeService:
    def __init__(
        self,
        repository: ResumeRepository,
        persona_repository: PersonaRepository,
        # job_repository: JobRepository = None,  # For future integration
        # job_analyzer: JobAnalyzer = None       # For future integration
    ):
        self._repository = repository
        self._persona_repo = persona_repository
        # self._job_repo = job_repository
        # self._job_analyzer = job_analyzer

    async def create_resume(
        self,
        user_id: str,
        name: str,
        target_role: str | None = None,
        target_job_id: str | None = None,
    ) -> Resume:
        """
        Create a new resume from the user's Persona.

        If target_job_id is provided, the resume will be pre-optimized
        for that job using AI suggestions (still grounded in Persona facts).
        """
        persona = await self._persona_repo.get_by_user_id(UUID(user_id))

        if not persona:
            raise ValueError("Please complete your profile first")

        # Create initial content selection (all experiences, skills, etc.)
        content_selection = self._create_initial_selection(persona, target_role)

        # If targeting a specific job, optimize selection
        if target_job_id:
            # Note: In a real implementation, we would fetch the job and analyze it
            # For now, we'll implement the logic structure as requested
            content_selection = await self._optimize_for_job(
                content_selection, persona, target_job_id
            )

        resume = Resume(
            user_id=UUID(user_id),
            persona_id=persona.id,
            name=name,
            target_role=target_role,
            content_selection=content_selection,
            version=1,
        )

        return await self._repository.save(resume)

    def _create_initial_selection(
        self, persona: Persona, target_role: str | None
    ) -> dict[str, Any]:
        """Create initial content selection from Persona"""
        return {
            "summary": "active",  # Use the active summary version
            "experiences": [str(e.id) for e in persona.experiences[:5]],  # Top 5
            "experience_versions": {
                str(e.id): "active" for e in persona.experiences[:5]
            },
            "education": [str(e.id) for e in persona.educations],
            "skills": {
                "selected": [str(s.id) for s in persona.get_verified_skills()],
                "order": None,  # Use default ordering
                "display_mode": "categorized",
            },
            "certifications": [str(c.id) for c in persona.certifications],
            "projects": [str(p.id) for p in persona.projects[:3]],
        }

    async def _optimize_for_job(
        self, selection: dict[str, Any], persona: Persona, target_job_id: str
    ) -> dict[str, Any]:
        """
        Optimize content selection for a specific job.

        This uses AI but is GROUNDED in existing Persona content.
        It only reorders and selects - never fabricates.
        """
        # Placeholder for job requirements extraction
        # In a real scenario: job_requirements = await self._job_analyzer.extract_requirements(job)
        job_requirements = ["leadership", "python", "fastapi", "system architecture"]

        # Score each experience for relevance
        experience_scores = []
        for exp in persona.experiences:
            score = self._score_experience_relevance(exp, job_requirements)
            experience_scores.append((exp, score))

        # Sort by relevance
        experience_scores.sort(key=lambda x: x[1], reverse=True)

        # Select top relevant experiences
        selected_experiences = [str(e[0].id) for e in experience_scores[:5]]

        # For enhanced versions, prefer enhanced if available
        experience_versions = {
            str(e[0].id): "enhanced" if e[0].description_enhanced else "active"
            for e in experience_scores[:5]
        }

        # Score and order skills by relevance
        skill_scores = []
        for skill in persona.get_verified_skills():
            relevance = self._calculate_skill_relevance(skill, job_requirements)
            skill_scores.append((skill, relevance))

        skill_scores.sort(key=lambda x: x[1], reverse=True)

        return {
            **selection,
            "experiences": selected_experiences,
            "experience_versions": experience_versions,
            "skills": {
                "selected": [str(s[0].id) for s in skill_scores if s[1] > 0.3],
                "order": [str(s[0].id) for s in skill_scores if s[1] > 0.3],
                "display_mode": "categorized",
            },
        }

    def _score_experience_relevance(
        self, experience: Experience, requirements: list[str]
    ) -> float:
        """Simple keyword-based relevance scoring for experience."""
        text = (
            f"{experience.job_title} {experience.description_active} "
            f"{' '.join(experience.bullets_active)}"
        ).lower()
        score = 0.0
        for req in requirements:
            if req.lower() in text:
                score += 1.0
        return score

    def _calculate_skill_relevance(
        self, skill: Skill, requirements: list[str]
    ) -> float:
        """Calculate relevance of a skill to job requirements."""
        if any(req.lower() in skill.name.lower() for req in requirements):
            return 1.0 + (skill.proficiency_level / 5.0)
        return 0.0

    async def get_resume(self, resume_id: UUID) -> Resume | None:
        return await self._repository.get_by_id(resume_id)

    async def get_user_resumes(self, user_id: UUID) -> list[Resume]:
        return await self._repository.get_all_by_user_id(user_id)

    async def update_resume(self, resume_id: UUID, schema: ResumeUpdate) -> Resume:
        resume = await self._repository.get_by_id(resume_id)
        if not resume:
            raise ValueError("Resume not found")

        if schema.name is not None:
            resume.name = schema.name
        if schema.target_role is not None:
            resume.target_role = schema.target_role
        if schema.target_industry is not None:
            resume.target_industry = schema.target_industry
        if schema.target_company is not None:
            resume.target_company = schema.target_company
        if schema.content_selection is not None:
            resume.content_selection = schema.content_selection
        if schema.template_id is not None:
            resume.template_id = schema.template_id
        if schema.is_primary is not None:
            resume.is_primary = schema.is_primary
        if schema.ats_score is not None:
            resume.ats_score = schema.ats_score

        resume.version += 1
        return await self._repository.save(resume)

    async def delete_resume(self, resume_id: UUID) -> None:
        await self._repository.delete(resume_id)

    async def render_resume(self, resume_id: UUID) -> RenderedResume:
        """
        Render a complete resume from the selection.
        Pulls actual content from Persona based on content_selection.
        """
        resume = await self._repository.get_by_id(resume_id)
        if not resume:
            raise ValueError("Resume not found")

        persona = await self._persona_repo.get_by_id(resume.persona_id)
        if not persona:
            raise ValueError("Persona not found")

        # 1. Header
        header = RenderedHeader(
            name=persona.full_name,
            email=persona.email,
            phone=persona.phone,
            location=f"{persona.location_city}, {persona.location_state}"
            if persona.location_city
            else None,
            linkedin=persona.linkedin_url,
            github=persona.github_url,
            portfolio=persona.portfolio_url,
        )

        # 2. Summary
        summary_type = resume.content_selection.get("summary", "active")
        if summary_type == "original":
            summary = persona.summary_original
        elif summary_type == "enhanced":
            summary = persona.summary_enhanced
        elif summary_type == "custom":
            summary = resume.content_selection.get("summary_custom")
        else:
            summary = persona.summary_active

        # 3. Experiences
        experiences = []
        for exp_id in resume.content_selection.get("experiences", []):
            desc, bullets = resume.get_experience_content(exp_id)
            exp = next((e for e in persona.experiences if str(e.id) == exp_id), None)
            if exp:
                experiences.append(
                    RenderedExperience(
                        id=exp.id,
                        company_name=exp.company_name,
                        job_title=exp.job_title,
                        location=exp.location,
                        start_date=exp.start_date.isoformat(),
                        end_date=exp.end_date.isoformat()
                        if exp.end_date
                        else "Present",
                        description=desc,
                        bullets=bullets,
                    )
                )

        # 4. Education
        education = []
        for edu_id in resume.content_selection.get("education", []):
            edu = next((e for e in persona.educations if str(e.id) == edu_id), None)
            if edu:
                education.append(
                    RenderedEducation(
                        id=edu.id,
                        institution_name=edu.institution_name,
                        degree_type=str(edu.degree_type),
                        field_of_study=edu.field_of_study,
                        graduation_date=edu.graduation_date.isoformat(),
                    )
                )

        # 5. Skills
        skills = []
        selected_skill_ids = resume.content_selection.get("skills", {}).get(
            "selected", []
        )
        for s_id in selected_skill_ids:
            skill = next((s for s in persona.skills if str(s.id) == s_id), None)
            if skill:
                skills.append(
                    RenderedSkill(name=skill.name, level=skill.proficiency_level)
                )

        return RenderedResume(
            header=header,
            summary=summary,
            experiences=experiences,
            education=education,
            skills=skills,
            certifications=[],
        )
