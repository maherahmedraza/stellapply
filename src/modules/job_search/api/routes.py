from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.job_search.api.schemas import (
    JobMatchResponse,
    JobResponse,
)
from src.modules.job_search.domain.services import JobSearchService
from src.modules.job_search.infrastructure.repository import SQLAlchemyJobRepository

router = APIRouter()


async def get_job_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> JobSearchService:
    repository = SQLAlchemyJobRepository(db)
    return JobSearchService(repository)


@router.get("/jobs", response_model=list[JobResponse])
async def search_jobs(
    query: str | None = None,
    location: str | None = None,
    remote_only: bool = False,
    salary_min: int | None = None,
    limit: int = 20,
    offset: int = 0,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: JobSearchService = Depends(get_job_service),  # noqa: B008
) -> list[JobResponse]:
    """
    Search jobs with location-based filtering.

    - **query**: Keywords to search in job titles/descriptions
    - **location**: Target location (city, state, or country)
    - **remote_only**: Filter to remote-only positions
    - **salary_min**: Minimum salary filter
    """
    jobs = await service.search_jobs(
        query=query,
        location=location,
        remote_only=remote_only,
        salary_min=salary_min,
        limit=limit,
        offset=offset,
    )
    return [JobResponse.model_validate(j) for j in jobs]


@router.get("/matches", response_model=list[JobMatchResponse])
async def list_matches(
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: JobSearchService = Depends(get_job_service),  # noqa: B008
) -> list[JobMatchResponse]:
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    matches = await service.get_user_matches(
        user_id=UUID(user_id_str), status=status, limit=limit, offset=offset
    )
    return [JobMatchResponse.model_validate(m) for m in matches]


@router.post("/jobs/{job_id}/match", response_model=JobMatchResponse)
async def analyze_match(
    job_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: JobSearchService = Depends(get_job_service),  # noqa: B008
) -> JobMatchResponse:
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    try:
        match = await service.match_job_for_user(UUID(user_id_str), job_id)
        return JobMatchResponse.model_validate(match)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
