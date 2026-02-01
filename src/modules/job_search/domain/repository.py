from typing import Protocol, runtime_checkable
from uuid import UUID

from src.modules.job_search.domain.models import Job, JobMatch


@runtime_checkable
class JobRepository(Protocol):
    async def get_by_id(self, job_id: UUID) -> Job | None: ...

    async def get_by_external_id(self, external_id: str) -> Job | None: ...

    async def save(self, job: Job) -> Job: ...

    async def search_jobs(
        self,
        query: str | None = None,
        embedding: list[float] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Job]: ...

    async def get_match(self, user_id: UUID, job_id: UUID) -> JobMatch | None: ...

    async def save_match(self, match: JobMatch) -> JobMatch: ...

    async def get_user_matches(
        self, user_id: UUID, status: str | None = None, limit: int = 20, offset: int = 0
    ) -> list[JobMatch]: ...
