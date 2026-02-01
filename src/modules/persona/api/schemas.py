from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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


class PersonaBase(BaseModel):
    preferred_name: str | None = None
    pronouns: str | None = None
    location: dict[str, Any] = Field(default_factory=dict)
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    skills: dict[str, Any] = Field(default_factory=dict)


class PersonaCreate(PersonaBase):
    user_id: UUID


class PersonaUpdate(PersonaBase):
    pass


class PersonaResponse(PersonaBase):
    id: UUID
    user_id: UUID
    completeness_score: int

    model_config = ConfigDict(from_attributes=True)
