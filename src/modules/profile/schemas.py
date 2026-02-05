import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

# --- Sub-Schemas ---


class AddressSchema(BaseModel):
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None


class PersonalInfoSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: date | None = None
    nationality: str | None = None
    gender: str | None = None
    salutation: str | None = None
    address: AddressSchema | None = None
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None
    website_url: HttpUrl | None = None
    work_authorization: str | None = None
    drivers_license: str | None = None
    willing_to_relocate: bool | None = None
    profile_photo_path: str | None = None


class ExperienceSchema(BaseModel):
    company: str
    title: str
    location: str | None = None
    start_date: date
    end_date: date | None = None  # None = current
    is_current: bool = False
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    employment_type: str | None = None  # full_time, part_time, contract, internship


class EducationSchema(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: date | None = None
    graduation_date: date | None = None
    gpa: str | None = None
    honors: str | None = None
    thesis_title: str | None = None
    relevant_coursework: list[str] = Field(default_factory=list)


class LanguageSchema(BaseModel):
    language: str
    proficiency: str  # native, fluent, advanced, intermediate, basic, A1-C2


class CertificationSchema(BaseModel):
    name: str
    issuer: str
    date_obtained: date | None = None
    expiry_date: date | None = None
    credential_id: str | None = None
    url: HttpUrl | None = None


class SearchPreferencesSchema(BaseModel):
    target_roles: list[str]
    target_industries: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    remote_preference: Literal["remote_only", "hybrid", "onsite", "flexible"] = (
        "flexible"
    )
    job_types: list[str] = Field(default_factory=lambda: ["full_time"])
    min_salary: int | None = None
    max_salary: int | None = None
    salary_currency: str = "EUR"
    company_size_preference: list[str] = Field(default_factory=list)
    excluded_companies: list[str] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=list)
    min_experience_match: float = 0.6
    max_commute_minutes: int | None = None
    start_date_earliest: date | None = None


class AgentRulesSchema(BaseModel):
    """User-defined rules that govern agent behavior."""

    auto_apply: bool = False
    max_applications_per_day: int = 10
    max_applications_per_week: int = 30
    skip_if_requires_cover_letter: bool = False
    skip_if_requires_assessment: bool = True
    skip_if_salary_below: int | None = None
    preferred_application_language: str = "en"
    apply_schedule: dict = Field(
        default_factory=lambda: {
            "days": ["mon", "tue", "wed", "thu", "fri"],
            "hours": {"start": 9, "end": 18},
        }
    )
    always_upload_resume: bool = True
    always_upload_cover_letter: bool = False
    custom_rules: list[str] = Field(default_factory=list)


class ApplicationAnswersSchema(BaseModel):
    """Pre-configured answers to common application questions."""

    salary_expectation: str | None = None
    earliest_start_date: str | None = None
    years_of_experience: str | None = None
    willing_to_travel: str | None = None
    require_sponsorship: str | None = None
    notice_period: str | None = None
    why_interested_template: str | None = None
    cover_letter_default: str | None = None
    strengths: str | None = None
    custom_answers: dict[str, str] = Field(default_factory=dict)
    pattern_answers: dict[str, str] = Field(default_factory=dict)


class ResumeStrategySchema(BaseModel):
    default_resume_id: uuid.UUID | None = None
    role_specific_resumes: dict[str, uuid.UUID] = Field(default_factory=dict)
    auto_tailor: bool = True


# --- Full Profile & API Models ---


class FullProfile(BaseModel):
    """Complete profile used by the agent."""

    personal_info: PersonalInfoSchema
    experience: list[ExperienceSchema] = Field(default_factory=list)
    education: list[EducationSchema] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    languages: list[LanguageSchema] = Field(default_factory=list)
    certifications: list[CertificationSchema] = Field(default_factory=list)
    search_preferences: SearchPreferencesSchema
    agent_rules: AgentRulesSchema
    application_answers: ApplicationAnswersSchema
    resume_strategy: ResumeStrategySchema
    resume_file_path: str | None = None
    cover_letter_file_path: str | None = None


class ProfileCompletenessReport(BaseModel):
    overall_score: float
    sections: dict[str, dict]  # e.g. {"personal_info": {"score": 90, "missing": [...]}}
    critical_missing: list[str]
    recommendations: list[str]


# --- Wrappers for API Responses (Backward Compatibility aliases) ---
# We keep UserProfileResponse matching FullProfile structure but with DB metadata


class UserProfileResponse(FullProfile):
    id: uuid.UUID
    user_id: uuid.UUID
    completeness: float = 0.0
    created_at: date  # Simplified from datetime for schema match, or keep datetime
    updated_at: date  # ditto

    model_config = ConfigDict(from_attributes=True)

    # Override validators if needed for datetime->date conversion


class UserProfileUpdate(BaseModel):
    """Allow partial updates to any section"""

    personal_info: PersonalInfoSchema | None = None
    experience: list[ExperienceSchema] | None = None
    education: list[EducationSchema] | None = None
    skills: list[str] | None = None
    languages: list[LanguageSchema] | None = None
    certifications: list[CertificationSchema] | None = None
    search_preferences: SearchPreferencesSchema | None = None
    agent_rules: AgentRulesSchema | None = None
    application_answers: ApplicationAnswersSchema | None = None
    resume_strategy: ResumeStrategySchema | None = None


class UserProfileCreate(BaseModel):
    """Initial creation schema"""

    personal_info: PersonalInfoSchema
    search_preferences: SearchPreferencesSchema
    agent_rules: AgentRulesSchema
    application_answers: ApplicationAnswersSchema
    resume_strategy: ResumeStrategySchema
