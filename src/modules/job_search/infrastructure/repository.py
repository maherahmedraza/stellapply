from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.modules.job_search.domain.models import Job, JobMatch
from src.modules.job_search.domain.repository import JobRepository


class SQLAlchemyJobRepository(JobRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, job_id: UUID) -> Job | None:
        result = await self._session.execute(
            select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> Job | None:
        result = await self._session.execute(
            select(Job).where(Job.external_id == external_id, Job.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def save(self, job: Job) -> Job:
        self._session.add(job)
        await self._session.flush()
        return job

    async def search_jobs(
        self,
        query: str | None = None,
        embedding: list[float] | None = None,
        location: str | None = None,
        remote_only: bool = False,
        salary_min: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Job]:
        stmt = select(Job).where(Job.deleted_at.is_(None))

        # Text search filter
        if query:
            stmt = stmt.where(
                (Job.title.ilike(f"%{query}%"))
                | (Job.company.ilike(f"%{query}%"))
                | (Job.description.ilike(f"%{query}%"))
            )

        # Location filter
        if location:
            stmt = stmt.where(Job.location.ilike(f"%{location}%"))

        # Remote-only filter
        if remote_only:
            stmt = stmt.where(
                (Job.work_setting == "remote") | (Job.location.ilike("%remote%"))
            )

        # Minimum salary filter
        if salary_min:
            stmt = stmt.where(
                (Job.salary_min >= salary_min) | (Job.salary_max >= salary_min)
            )

        # Ordering: vector similarity or recency
        if embedding:
            # Vector similarity search using pgvector
            stmt = stmt.order_by(Job.description_embedding.cosine_distance(embedding))
        else:
            stmt = stmt.order_by(Job.posted_at.desc())

        result = await self._session.execute(stmt.limit(limit).offset(offset))
        return list(result.scalars().all())

    async def get_match(self, user_id: UUID, job_id: UUID) -> JobMatch | None:
        result = await self._session.execute(
            select(JobMatch)
            .where(
                JobMatch.user_id == user_id,
                JobMatch.job_id == job_id,
                JobMatch.deleted_at.is_(None),
            )
            .options(joinedload(JobMatch.job))
        )
        return result.scalar_one_or_none()

    async def save_match(self, match: JobMatch) -> JobMatch:
        self._session.add(match)
        await self._session.flush()
        return match

    async def get_user_matches(
        self, user_id: UUID, status: str | None = None, limit: int = 20, offset: int = 0
    ) -> list[JobMatch]:
        stmt = (
            select(JobMatch)
            .where(JobMatch.user_id == user_id, JobMatch.deleted_at.is_(None))
            .options(joinedload(JobMatch.job))
        )

        if status:
            stmt = stmt.where(JobMatch.status == status)

        stmt = stmt.order_by(JobMatch.overall_score.desc())

        result = await self._session.execute(stmt.limit(limit).offset(offset))
        return list(result.scalars().all())
