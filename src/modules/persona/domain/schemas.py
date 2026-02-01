import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.modules.persona.domain.models import (
    CompanySize,
    DegreeType,
    QuestionType,
    RemotePreference,
    SkillCategory,
    WorkAuthorization,
)


# --- Experience Schemas ---
class ExperienceBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    job_title: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date | None = None
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)
    skills_used: list[str] = Field(default_factory=list)


class ExperienceCreate(ExperienceBase):
    experience_embedding: list[float] | None = None


class ExperienceUpdate(BaseModel):
    company_name: str | None = None
    job_title: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    achievements: list[str] | None = None
    skills_used: list[str] | None = None
    experience_embedding: list[float] | None = None


class ExperienceRead(ExperienceBase):
    id: uuid.UUID
    persona_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# --- Education Schemas ---
class EducationBase(BaseModel):
    institution_name: str = Field(..., min_length=1, max_length=255)
    degree_type: DegreeType
    field_of_study: str = Field(..., min_length=1, max_length=255)
    graduation_date: date
    gpa: float | None = Field(None, ge=0.0, le=4.0)


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution_name: str | None = None
    degree_type: DegreeType | None = None
    field_of_study: str | None = None
    graduation_date: date | None = None
    gpa: float | None = None


class EducationRead(EducationBase):
    id: uuid.UUID
    persona_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# --- Skill Schemas ---
class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: SkillCategory = SkillCategory.TECHNICAL
    proficiency_level: int = Field(1, ge=1, le=5)


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: str | None = None
    category: SkillCategory | None = None
    proficiency_level: int | None = None


class SkillRead(SkillBase):
    id: uuid.UUID
    persona_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# --- Career Preference Schemas ---
class CareerPreferenceBase(BaseModel):
    target_titles: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    company_sizes: list[CompanySize] = Field(default_factory=list)
    blacklisted_companies: list[str] = Field(default_factory=list)
    dream_companies: list[str] = Field(default_factory=list)


class CareerPreferenceCreate(CareerPreferenceBase):
    pass


class CareerPreferenceUpdate(CareerPreferenceBase):
    pass


class CareerPreferenceRead(CareerPreferenceBase):
    id: uuid.UUID
    persona_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# --- Behavioral Answer Schemas ---
class BehavioralAnswerBase(BaseModel):
    question_type: QuestionType
    answer: str = Field(..., min_length=1)


class BehavioralAnswerCreate(BehavioralAnswerBase):
    answer_embedding: list[float] | None = None


class BehavioralAnswerRead(BehavioralAnswerBase):
    id: uuid.UUID
    persona_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# --- Persona Schemas ---
class PersonaBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)
    location_city: str | None = Field(None, max_length=100)
    location_state: str | None = Field(None, max_length=100)
    location_country: str | None = Field(None, max_length=100)
    work_authorization: WorkAuthorization = WorkAuthorization.NOT_REQUIRED
    remote_preference: RemotePreference = RemotePreference.ANY


class PersonaCreate(PersonaBase):
    user_id: uuid.UUID
    summary_embedding: list[float] | None = None


class PersonaUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    location_city: str | None = None
    location_state: str | None = None
    location_country: str | None = None
    work_authorization: WorkAuthorization | None = None
    remote_preference: RemotePreference | None = None
    summary_embedding: list[float] | None = None
    completeness_score: float | None = None


class PersonaRead(PersonaBase):
    id: uuid.UUID
    user_id: uuid.UUID
    completeness_score: float
    created_at: datetime
    updated_at: datetime

    # Nested relations
    experiences: list[ExperienceRead] = Field(default_factory=list)
    educations: list[EducationRead] = Field(default_factory=list)
    skills: list[SkillRead] = Field(default_factory=list)
    career_preference: CareerPreferenceRead | None = None
    behavioral_answers: list[BehavioralAnswerRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
