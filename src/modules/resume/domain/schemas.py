import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.modules.resume.domain.models import (
    ResumeSource,
    SectionType,
    TemplateCategory,
)


# --- ResumeTemplate Schemas ---
class ResumeTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    thumbnail_url: HttpUrl | None = None
    category: TemplateCategory = TemplateCategory.CLASSIC
    is_ats_optimized: bool = True
    settings: dict[str, Any] = Field(default_factory=dict)


class ResumeTemplateCreate(ResumeTemplateBase):
    template_file: str = Field(..., description="Jinja2 template content")


class ResumeTemplateRead(ResumeTemplateBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# --- ResumeSection Schemas ---
class ResumeSectionBase(BaseModel):
    section_type: SectionType
    order: int = 0
    content: dict[str, Any] = Field(default_factory=dict)
    is_visible: bool = True


class ResumeSectionCreate(ResumeSectionBase):
    pass


class ResumeSectionRead(ResumeSectionBase):
    id: uuid.UUID
    resume_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# --- ATSAnalysis Schemas ---
class ATSAnalysisBase(BaseModel):
    job_id: uuid.UUID | None = None
    overall_score: float = Field(..., ge=0, le=100)
    format_score: float | None = Field(None, ge=0, le=100)
    content_score: float | None = Field(None, ge=0, le=100)
    keyword_score: float | None = Field(None, ge=0, le=100)
    recommendations: list[str] = Field(default_factory=list)


class ATSAnalysisRead(ATSAnalysisBase):
    id: uuid.UUID
    resume_id: uuid.UUID
    analyzed_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- ResumeVersion Schemas ---
class ResumeVersionBase(BaseModel):
    version_number: int
    content_snapshot: dict[str, Any]
    change_summary: str | None = None


class ResumeVersionRead(ResumeVersionBase):
    id: uuid.UUID
    resume_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Resume Schemas ---
class ResumeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    persona_id: uuid.UUID
    target_role: str | None = Field(None, max_length=100)
    target_industry: str | None = Field(None, max_length=100)
    target_company: str | None = Field(None, max_length=100)
    content_selection: dict[str, Any] = Field(default_factory=dict)
    content: dict[str, Any] = Field(default_factory=dict)
    is_primary: bool = False
    template_id: uuid.UUID | None = None
    created_from: ResumeSource = ResumeSource.SCRATCH
    target_job_id: uuid.UUID | None = None


class ResumeCreate(ResumeBase):
    user_id: uuid.UUID


class ResumeUpdate(BaseModel):
    name: str | None = None
    target_role: str | None = None
    target_industry: str | None = None
    target_company: str | None = None
    content_selection: dict[str, Any] | None = None
    content: dict[str, Any] | None = None
    is_primary: bool | None = None
    template_id: uuid.UUID | None = None
    ats_score: float | None = None
    word_count: int | None = None
    file_path: str | None = None


class ResumeRead(ResumeBase):
    id: uuid.UUID
    user_id: uuid.UUID
    version: int
    ats_score: float | None = None
    word_count: int | None = None
    file_path: str | None = None
    created_at: datetime
    updated_at: datetime

    # Nested relations
    sections: list[ResumeSectionRead] = Field(default_factory=list)
    ats_analyses: list[ATSAnalysisRead] = Field(default_factory=list)
    versions: list[ResumeVersionRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Rendered Resume Schemas (for UI/Export) ---
class RenderedHeader(BaseModel):
    name: str
    email: str
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None


class RenderedExperience(BaseModel):
    id: uuid.UUID
    company_name: str
    job_title: str
    location: str | None = None
    start_date: str
    end_date: str | None = None
    description: str | None = None
    bullets: list[str] = Field(default_factory=list)


class RenderedEducation(BaseModel):
    id: uuid.UUID
    institution_name: str
    degree_type: str
    field_of_study: str
    graduation_date: str


class RenderedSkill(BaseModel):
    name: str
    level: int | None = None


class RenderedResume(BaseModel):
    header: RenderedHeader
    summary: str | None = None
    experiences: list[RenderedExperience] = Field(default_factory=list)
    education: list[RenderedEducation] = Field(default_factory=list)
    skills: list[RenderedSkill] = Field(default_factory=list)
    certifications: list[dict[str, Any]] = Field(default_factory=list)
