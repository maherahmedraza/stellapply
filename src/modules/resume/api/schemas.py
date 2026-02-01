from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResumeSection(BaseModel):
    title: str | None = None
    content: str | None = None


class ResumeExperience(BaseModel):
    title: str
    company: str
    location: str | None = None
    start_date: str | None = None  # Flexible string for parsed dates
    end_date: str | None = None
    description: str | None = None
    highlights: list[str] = Field(default_factory=list)


class ResumeEducation(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    location: str | None = None
    end_date: str | None = None


class ResumeContent(BaseModel):
    summary: str | None = None
    experience: list[ResumeExperience] = Field(default_factory=list)
    education: list[ResumeEducation] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    custom_sections: dict[str, Any] = Field(default_factory=dict)


class ResumeBase(BaseModel):
    name: str
    template_id: str | None = None
    content: ResumeContent
    is_primary: bool = False


class ResumeCreate(ResumeBase):
    user_id: UUID


class ResumeUpdate(BaseModel):
    name: str | None = None
    template_id: str | None = None
    content: ResumeContent | None = None
    is_primary: bool | None = None


class ResumeResponse(ResumeBase):
    id: UUID
    user_id: UUID
    ats_score: int | None = None
    analysis_results: dict[str, Any] = Field(default_factory=dict)
    analyzed_at: datetime | None = None
    pdf_url: str | None = None
    docx_url: str | None = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
