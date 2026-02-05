from datetime import datetime
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field, EmailStr, HttpUrl


class AddressSchema(BaseModel):
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


class PersonalInfoSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    date_of_birth: str | None = None
    nationality: str | None = None
    address: AddressSchema | None = None
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None
    visa_status: str | None = None
    work_authorization: str | None = None
    gender: str | None = None
    disability_status: str | None = None
    veteran_status: str | None = None


class LocationPreference(BaseModel):
    city: str
    country: str
    radius_km: int = 25


class SalaryExpectations(BaseModel):
    min: int
    max: int
    currency: str = "EUR"
    period: Literal["annual", "monthly", "hourly"] = "annual"
    negotiable: bool = True


class SearchPreferencesSchema(BaseModel):
    target_roles: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)
    experience_level: Literal["junior", "mid", "senior", "lead", "executive"] | None = (
        None
    )
    job_types: list[str] = Field(default_factory=list)  # full_time, contract, etc.
    remote_preference: Literal["onsite", "hybrid", "remote", "any"] = "hybrid"
    locations: list[LocationPreference] = Field(default_factory=list)
    willing_to_relocate: bool = False
    salary_expectations: SalaryExpectations | None = None
    start_date: str | None = None
    notice_period: str | None = None
    company_size_preference: list[str] = Field(default_factory=list)
    languages_required: list[str] = Field(default_factory=list)
    travel_tolerance: str | None = None


class AgentRulesSchema(BaseModel):
    max_applications_per_day: int = 10
    max_applications_per_week: int = 40
    blacklisted_companies: list[str] = Field(default_factory=list)
    blacklisted_domains: list[str] = Field(default_factory=list)
    require_salary_listed: bool = False
    min_match_score: int = 70
    auto_apply: bool = True
    pause_on_weekends: bool = True
    preferred_application_hours: str = "09:00-18:00"
    skip_cover_letter_if_optional: bool = False
    cover_letter_tone: str = "professional"
    answer_optional_questions: bool = True
    preferred_job_boards: list[str] = Field(default_factory=list)


class ApplicationAnswersSchema(BaseModel):
    why_interested_template: str | None = None
    greatest_strength: str | None = None
    greatest_weakness: str | None = None
    where_see_yourself_5_years: str | None = None
    why_leaving_current: str | None = None
    earliest_start_date: str | None = None
    referral_source: str | None = None
    how_did_you_hear: str = "Job Board"
    custom_answers: dict[str, str] = Field(default_factory=dict)


class ResumeStrategySchema(BaseModel):
    default_resume_id: uuid.UUID | None = None
    role_specific_resumes: dict[str, uuid.UUID] = Field(default_factory=dict)
    auto_tailor: bool = True


class UserProfileBase(BaseModel):
    pass


class UserProfileCreate(UserProfileBase):
    personal_info: PersonalInfoSchema
    search_preferences: SearchPreferencesSchema
    agent_rules: AgentRulesSchema
    application_answers: ApplicationAnswersSchema
    resume_strategy: ResumeStrategySchema


class UserProfileUpdate(BaseModel):
    personal_info: PersonalInfoSchema | None = None
    search_preferences: SearchPreferencesSchema | None = None
    agent_rules: AgentRulesSchema | None = None
    application_answers: ApplicationAnswersSchema | None = None
    resume_strategy: ResumeStrategySchema | None = None


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    personal_info: PersonalInfoSchema
    search_preferences: SearchPreferencesSchema
    agent_rules: AgentRulesSchema
    application_answers: ApplicationAnswersSchema
    resume_strategy: ResumeStrategySchema
    completeness: float = 0.0  # Computed field
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileCompletenessResponse(BaseModel):
    overall: float
    sections: dict[str, float]
    missing_fields: list[str]
