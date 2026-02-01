from datetime import datetime
from uuid import UUID

from src.modules.resume.api.schemas import ResumeContent, ResumeCreate, ResumeUpdate
from src.modules.resume.domain.models import Resume
from src.modules.resume.domain.repository import ResumeRepository


class ResumeService:
    def __init__(self, repository: ResumeRepository):
        self._repository = repository

    async def create_resume(self, schema: ResumeCreate) -> Resume:
        resume = Resume(
            user_id=schema.user_id,
            name=schema.name,
            template_id=schema.template_id,
            content=schema.content.model_dump(),
            is_primary=schema.is_primary,
            version=1,
        )
        return await self._repository.save(resume)

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
        if schema.template_id is not None:
            resume.template_id = schema.template_id
        if schema.content is not None:
            resume.content = schema.content.model_dump()
        if schema.is_primary is not None:
            resume.is_primary = schema.is_primary

        resume.version += 1
        return await self._repository.save(resume)

    async def delete_resume(self, resume_id: UUID) -> None:
        await self._repository.delete(resume_id)

    async def parse_resume_content(self, _raw_text: str) -> ResumeContent:
        # TODO: Integrate with Gemini for actual parsing
        # This is a placeholder for the AI parsing logic
        return ResumeContent(
            summary="Extracted summary placeholder",
            experience=[],
            education=[],
            skills=["Python", "FastAPI"],
            projects=[],
        )

    async def analyze_ats(self, resume_id: UUID) -> Resume:
        resume = await self._repository.get_by_id(resume_id)
        if not resume:
            raise ValueError("Resume not found")

        # TODO: Integrate with AI worker for ATS analysis
        resume.ats_score = 85
        resume.analysis_results = {
            "strengths": ["Clear structure", "Action-oriented language"],
            "weaknesses": ["Missing quantitative metrics in some bullets"],
            "recommendations": ["Add specific metrics for experience highlights"],
        }
        from datetime import UTC

        resume.analyzed_at = datetime.now(UTC)

        return await self._repository.save(resume)
