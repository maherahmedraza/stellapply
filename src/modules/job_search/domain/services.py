from uuid import UUID

from src.modules.job_search.api.schemas import JobMatchAnalysis
from src.modules.job_search.domain.models import Job, JobMatch
from src.modules.job_search.domain.repository import JobRepository


class JobSearchService:
    def __init__(self, repository: JobRepository):
        self._repository = repository

    async def get_job(self, job_id: UUID) -> Job | None:
        return await self._repository.get_by_id(job_id)

    async def search_jobs(
        self,
        query: str | None = None,
        embedding: list[float] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Job]:
        return await self._repository.search_jobs(query, embedding, limit, offset)

    async def get_user_matches(
        self, user_id: UUID, status: str | None = None, limit: int = 20, offset: int = 0
    ) -> list[JobMatch]:
        return await self._repository.get_user_matches(user_id, status, limit, offset)

    async def update_match_status(self, match_id: UUID, status: str) -> JobMatch:
        # In a real app, we'd fetch the match by ID first.
        # For now, let's assume we have a way to fetch/update match status.
        # This logic is simplified for the current scope.
        raise NotImplementedError("Match status update not fully implemented")

    async def match_job_for_user(self, user_id: UUID, job_id: UUID) -> JobMatch:
        job = await self._repository.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")

        # Check if match already exists
        existing_match = await self._repository.get_match(user_id, job_id)
        if existing_match:
            return existing_match

        # Placeholder for AI-powered matching logic
        # 1. Fetch user persona/resume embeddings
        # 2. Compare with job description embedding (vector score)
        # 3. Use Gemini to analyze deep fit (strengths, weaknesses)

        analysis = JobMatchAnalysis(
            strengths=["Matches core skills", "Location alignment"],
            weaknesses=["Missing specific framework experience"],
            fit_explanation=(
                "Your background in Python and FastAPI makes you a strong "
                "candidate for this role."
            ),
            missing_skills=["Kubernetes"],
        )

        match = JobMatch(
            user_id=user_id,
            job_id=job_id,
            overall_score=85,
            vector_score=0.92,
            analysis=analysis.model_dump(),
            status="pending",
        )

        return await self._repository.save_match(match)
