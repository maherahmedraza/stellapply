from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.resume.domain.models import Resume, ResumeTemplate
from src.modules.resume.domain.repository import ResumeRepository


from sqlalchemy.orm import selectinload


class SQLAlchemyResumeRepository(ResumeRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, resume_id: UUID) -> Resume | None:
        result = await self._session.execute(
            select(Resume)
            .options(
                selectinload(Resume.sections),
                selectinload(Resume.ats_analyses),
                selectinload(Resume.versions),
            )
            .where(Resume.id == resume_id, Resume.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, user_id: UUID) -> list[Resume]:
        result = await self._session.execute(
            select(Resume)
            .options(
                selectinload(Resume.sections),
                selectinload(Resume.ats_analyses),
                selectinload(Resume.versions),
            )
            .where(Resume.user_id == user_id, Resume.deleted_at.is_(None))
            .order_by(Resume.updated_at.desc())
        )
        return list(result.scalars().all())

    async def get_primary_by_user_id(self, user_id: UUID) -> Resume | None:
        result = await self._session.execute(
            select(Resume)
            .options(
                selectinload(Resume.sections),
                selectinload(Resume.ats_analyses),
                selectinload(Resume.versions),
            )
            .where(
                Resume.user_id == user_id,
                Resume.is_primary,
                Resume.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def save(self, resume: Resume) -> Resume:
        if resume.is_primary:
            # Unset other primary resumes for this user
            await self._session.execute(
                update(Resume)
                .where(
                    Resume.user_id == resume.user_id,
                    Resume.is_primary,
                    Resume.id != resume.id,
                )
                .values(is_primary=False)
            )

        self._session.add(resume)
        await self._session.commit()

        # Re-fetch with relationships
        return await self.get_by_id(resume.id)

    async def delete(self, resume_id: UUID) -> None:
        resume = await self.get_by_id(resume_id)
        if resume:
            resume.soft_delete()
            self._session.add(resume)

    async def get_template_by_id(self, template_id: UUID) -> ResumeTemplate | None:
        result = await self._session.execute(
            select(ResumeTemplate).where(
                ResumeTemplate.id == template_id, ResumeTemplate.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_active_templates(self) -> list[ResumeTemplate]:
        result = await self._session.execute(
            select(ResumeTemplate).where(ResumeTemplate.deleted_at.is_(None))
        )
        return list(result.scalars().all())
