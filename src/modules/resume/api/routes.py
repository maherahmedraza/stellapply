import logging
from typing import Any
from uuid import UUID
import io
import re

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.resume.api.schemas import ResumeCreate, ResumeResponse, ResumeUpdate
from src.modules.resume.domain.schemas import RenderedResume
from src.modules.resume.domain.services import ResumeService
from src.modules.resume.infrastructure.repository import SQLAlchemyResumeRepository
from src.modules.persona.infrastructure.repository import SQLAlchemyPersonaRepository

logger = logging.getLogger(__name__)
router = APIRouter()


# =============== Resume Parse Response Schemas ===============


class ParsedPersonalInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    location: str | None = None


class ParsedExperience(BaseModel):
    title: str
    company: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    current: bool = False
    highlights: list[str] = []


class ParsedEducation(BaseModel):
    degree: str
    school: str
    field: str | None = None
    start_year: str | None = None
    end_year: str | None = None


class ResumeParseResponse(BaseModel):
    success: bool
    message: str
    personal_info: ParsedPersonalInfo | None = None
    experience: list[ParsedExperience] = []
    education: list[ParsedEducation] = []
    skills: list[str] = []
    summary: str | None = None


# =============== Resume Service Dependency ===============


async def get_resume_service(
    db: AsyncSession = Depends(get_db),
) -> ResumeService:
    repository = SQLAlchemyResumeRepository(db)
    persona_repository = SQLAlchemyPersonaRepository(db)
    return ResumeService(repository, persona_repository)


# =============== Resume CRUD Endpoints ===============


@router.get("/", response_model=list[ResumeResponse])
async def list_my_resumes(
    current_user: dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
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
    current_user: dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
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

    resume = await service.create_resume(
        user_id=user_id_str,
        name=schema.name,
        target_role=schema.target_role,
        target_job_id=str(schema.target_job_id) if schema.target_job_id else None,
    )
    return ResumeResponse.model_validate(resume)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
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
    current_user: dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
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
    current_user: dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
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


# =============== AI & Rendering Endpoints ===============


@router.post("/{resume_id}/analyze", response_model=ResumeResponse)
async def analyze_resume(
    resume_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
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


@router.get("/{resume_id}/render", response_model=RenderedResume)
async def render_resume(
    resume_id: UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
) -> RenderedResume:
    """Get the fully rendered resume content (grounded in Persona)."""
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

    return await service.render_resume(resume_id)


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Upload and parse a resume file using Gemini AI.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    file_ext = file.filename.lower().split(".")[-1]
    if file_ext not in ("pdf", "docx", "doc"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported",
        )

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit",
        )

    try:
        from src.core.ai.gemini_client import GeminiClient
        from src.core.config import settings
        from src.modules.resume.ai.resume_parser import ResumeParser

        # Use the correct setting name from our updated config
        gemini_client = GeminiClient(api_key=settings.ai.GEMINI_API_KEY)
        parser = ResumeParser(gemini_client)

        extracted = await parser.parse_resume(content, file.filename)
        form_data = parser.convert_to_form_data(extracted)

        return {
            "status": "success",
            "message": "Resume parsed successfully",
            "data": form_data,
        }
    except Exception as e:
        logger.error(f"Resume parsing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse resume. Please try again or enter data manually.",
        ) from e
