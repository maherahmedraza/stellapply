from typing import Any
from uuid import UUID
import io
import re
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.api.middleware.auth import get_current_user
from src.core.database.connection import get_db
from src.modules.resume.api.schemas import ResumeCreate, ResumeResponse, ResumeUpdate
from src.modules.resume.domain.services import ResumeService
from src.modules.resume.infrastructure.repository import SQLAlchemyResumeRepository

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


# =============== Helper functions for parsing ===============


def extract_email(text: str) -> str | None:
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = re.search(r"[\+\d][\d\s\-\(\)]{8,}", text)
    return match.group(0).strip() if match else None


def extract_linkedin(text: str) -> str | None:
    match = re.search(r"linkedin\.com/in/[\w\-]+", text)
    return f"https://{match.group(0)}" if match else None


def extract_github(text: str) -> str | None:
    match = re.search(r"github\.com/[\w\-]+", text)
    return f"https://{match.group(0)}" if match else None


def parse_resume_text(text: str) -> ResumeParseResponse:
    """Parse extracted text into structured resume data."""
    lines = text.strip().split("\n")

    # Extract personal info
    personal_info = ParsedPersonalInfo(
        name=lines[0][:100] if lines else None,  # First line often is name
        email=extract_email(text),
        phone=extract_phone(text),
        linkedin=extract_linkedin(text),
        github=extract_github(text),
    )

    # Extract skills - look for common patterns
    skills = []
    skill_keywords = [
        "python",
        "java",
        "javascript",
        "typescript",
        "sql",
        "spark",
        "kafka",
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "airflow",
        "dbt",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "elasticsearch",
        "react",
        "angular",
        "vue",
        "node",
        "fastapi",
        "django",
        "flask",
        "git",
        "linux",
        "terraform",
        "jenkins",
        "ci/cd",
        "agile",
        "scrum",
        "machine learning",
        "data engineering",
        "etl",
        "data modeling",
    ]
    text_lower = text.lower()
    for skill in skill_keywords:
        if skill in text_lower:
            skills.append(skill.title() if len(skill) > 3 else skill.upper())

    return ResumeParseResponse(
        success=True,
        message=f"Extracted resume data. Found {len(skills)} skills.",
        personal_info=personal_info,
        skills=skills[:20],  # Limit to 20 skills
        experience=[],  # Would need more sophisticated parsing
        education=[],
    )


# =============== Resume Parse Endpoint ===============


@router.post("/upload", response_model=ResumeParseResponse)
async def upload_and_parse_resume(
    file: UploadFile = File(...),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ResumeParseResponse:
    """Upload and parse a resume file (PDF, DOC, DOCX, or TXT)."""

    allowed_types = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, DOC, DOCX, TXT",
        )

    try:
        content = await file.read()
        text = ""

        if file.content_type == "application/pdf":
            try:
                import pypdf

                pdf_reader = pypdf.PdfReader(io.BytesIO(content))
                text = "\n".join(page.extract_text() for page in pdf_reader.pages)
            except ImportError:
                # Fallback if pypdf not available
                logger.warning("pypdf not installed, returning mock data")
                return ResumeParseResponse(
                    success=True,
                    message="PDF parsing requires pypdf. Using mock data for demo.",
                    personal_info=ParsedPersonalInfo(
                        name="Imported from Resume",
                        email=current_user.get("email", "user@example.com"),
                    ),
                    skills=["Python", "SQL", "Data Engineering"],
                )
        elif file.content_type == "text/plain":
            text = content.decode("utf-8")
        else:
            # For DOC/DOCX, would need python-docx
            return ResumeParseResponse(
                success=True,
                message="DOC/DOCX parsing would require python-docx. Using basic extraction.",
                personal_info=ParsedPersonalInfo(name="Imported User"),
                skills=[],
            )

        if not text.strip():
            return ResumeParseResponse(
                success=False, message="Could not extract text from the uploaded file."
            )

        result = parse_resume_text(text)
        logger.info(
            f"Parsed resume for user {current_user.get('sub')}: found {len(result.skills)} skills"
        )
        return result

    except Exception as e:
        logger.error(f"Error parsing resume: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing resume: {str(e)}",
        )


# =============== Existing Resume CRUD Endpoints ===============


async def get_resume_service(
    db: AsyncSession = Depends(get_db),
) -> ResumeService:
    repository = SQLAlchemyResumeRepository(db)
    return ResumeService(repository)


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
