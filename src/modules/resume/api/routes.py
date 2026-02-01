from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.resume.api.schemas import ResumeCreate, ResumeResponse, ResumeUpdate
from src.modules.resume.domain.services import ResumeService
from src.modules.resume.infrastructure.repository import SQLAlchemyResumeRepository

router = APIRouter()


async def get_resume_service(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> ResumeService:
    repository = SQLAlchemyResumeRepository(db)
    return ResumeService(repository)


@router.get("/", response_model=list[ResumeResponse])
async def list_my_resumes(
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: ResumeService = Depends(get_resume_service),  # noqa: B008
) -> list[ResumeResponse]:
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    user_id = UUID(user_id_str)
    resumes = await service.get_user_resumes(user_id)
    return [ResumeResponse.model_validate(r) for r in resumes]


@router.post("/", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    schema: ResumeCreate,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: ResumeService = Depends(get_resume_service),  # noqa: B008
) -> ResumeResponse:
    user_id_str = current_user.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    if UUID(user_id_str) != schema.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create resume for another user",
        )

    resume = await service.create_resume(schema)
    return ResumeResponse.model_validate(resume)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: ResumeService = Depends(get_resume_service),  # noqa: B008
) -> ResumeResponse:
    resume = await service.get_resume(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    user_id_str = current_user.get("sub")
    if user_id_str and resume.user_id != UUID(user_id_str):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return ResumeResponse.model_validate(resume)


@router.patch("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: UUID,
    schema: ResumeUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: ResumeService = Depends(get_resume_service),  # noqa: B008
) -> ResumeResponse:
    resume = await service.get_resume(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    user_id_str = current_user.get("sub")
    if user_id_str and resume.user_id != UUID(user_id_str):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    updated_resume = await service.update_resume(resume_id, schema)
    return ResumeResponse.model_validate(updated_resume)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: ResumeService = Depends(get_resume_service),  # noqa: B008
) -> None:
    resume = await service.get_resume(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    user_id_str = current_user.get("sub")
    if user_id_str and resume.user_id != UUID(user_id_str):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    await service.delete_resume(resume_id)


@router.post("/{resume_id}/analyze", response_model=ResumeResponse)
async def analyze_resume(
    resume_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),  # noqa: B008
    service: ResumeService = Depends(get_resume_service),  # noqa: B008
) -> ResumeResponse:
    resume = await service.get_resume(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )

    user_id_str = current_user.get("sub")
    if user_id_str and resume.user_id != UUID(user_id_str):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    analyzed_resume = await service.analyze_ats(resume_id)
    return ResumeResponse.model_validate(analyzed_resume)
