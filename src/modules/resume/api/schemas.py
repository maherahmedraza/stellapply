from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from src.modules.resume.domain.schemas import (
    ATSAnalysisBase,
    ATSAnalysisRead,
    ResumeBase,
    ResumeCreate,
    ResumeRead,
    ResumeSectionBase,
    ResumeSectionCreate,
    ResumeSectionRead,
    ResumeTemplateBase,
    ResumeTemplateCreate,
    ResumeTemplateRead,
    ResumeUpdate,
    ResumeVersionBase,
    ResumeVersionRead,
)


class ExperienceItem(BaseModel):
    title: str
    company: str
    location: str | None = None
    start_date: date
    end_date: date | None = None
    description: str | None = None
    is_current: bool = False


class EducationItem(BaseModel):
    institution: str
    degree: str
    field_of_study: str | None = None
    start_date: date
    end_date: date | None = None
    description: str | None = None


class ResumeContent(BaseModel):
    summary: str | None = None
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[Any] = Field(default_factory=list)


# Aliases for compatibility
ResumeResponse = ResumeRead

__all__ = [
    "ResumeContent",
    "ExperienceItem",
    "EducationItem",
    "ResumeBase",
    "ResumeCreate",
    "ResumeUpdate",
    "ResumeRead",
    "ResumeResponse",
    "ResumeTemplateBase",
    "ResumeTemplateCreate",
    "ResumeTemplateRead",
    "ResumeSectionBase",
    "ResumeSectionCreate",
    "ResumeSectionRead",
    "ATSAnalysisBase",
    "ATSAnalysisRead",
    "ResumeVersionBase",
    "ResumeVersionRead",
]
