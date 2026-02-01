from uuid import UUID

from src.modules.resume.domain.models import ATSAnalysis, Resume
from src.modules.resume.domain.repository import ResumeRepository
from src.modules.resume.domain.schemas import ResumeCreate, ResumeUpdate


class ResumeService:
    def __init__(self, repository: ResumeRepository):
        self._repository = repository

    async def create_resume(self, schema: ResumeCreate) -> Resume:
        resume = Resume(
            user_id=schema.user_id,
            name=schema.name,
            template_id=schema.template_id,
            content=schema.content,
            is_primary=schema.is_primary,
            version=1,
            created_from=schema.created_from,
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
            resume.content = schema.content
        if schema.is_primary is not None:
            resume.is_primary = schema.is_primary
        if schema.ats_score is not None:
            resume.ats_score = schema.ats_score
        if schema.word_count is not None:
            resume.word_count = schema.word_count
        if schema.file_path is not None:
            resume.file_path = schema.file_path

        resume.version += 1
        return await self._repository.save(resume)

    async def delete_resume(self, resume_id: UUID) -> None:
        await self._repository.delete(resume_id)

    async def analyze_ats(self, resume_id: UUID, job_id: UUID | None = None) -> Resume:
        resume = await self._repository.get_by_id(resume_id)
        if not resume:
            raise ValueError("Resume not found")

        # TODO: Integrate with AI worker for ATS analysis
        # For now, create a mock analysis record
        score = 85.0
        analysis = ATSAnalysis(
            resume_id=resume.id,
            job_id=job_id,
            overall_score=score,
            format_score=90.0,
            content_score=80.0,
            keyword_score=85.0,
            recommendations=[
                "Add specific metrics for experience highlights",
                "Tailor summary to job description",
            ],
        )
        resume.ats_score = score
        resume.ats_analyses.append(analysis)

        return await self._repository.save(resume)
