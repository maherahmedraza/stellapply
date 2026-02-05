from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobBase(BaseModel):
    title: str
    company: str
    location: str | None = None
    url: str
    description: str
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    job_type: str | None = None
    work_setting: str | None = None
    posted_at: datetime | None = None


class JobResponse(JobBase):
    id: UUID
    source: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobMatchAnalysis(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    fit_explanation: str | None = None
    missing_skills: list[str] = Field(default_factory=list)
    matching_skills: list[str] = Field(default_factory=list)
    skills_match_count: int = 0
    total_required_skills: int = 0


class JobMatchResponse(BaseModel):
    id: UUID
    job: JobResponse
    overall_score: int
    vector_score: float | None = None
    analysis: JobMatchAnalysis
    status: str
    created_at: datetime

    # LinkedIn-style match indicators
    is_top_applicant: bool = False  # True if 90%+ match
    match_percentile: int = 0  # e.g., "Top 5% of applicants"

    model_config = ConfigDict(from_attributes=True)


class JobSearchParams(BaseModel):
    """Parameters for location-based job search."""

    query: str | None = None
    location: str | None = None
    remote_only: bool = False
    radius_miles: int = 50
    salary_min: int | None = None
    use_persona_preferences: bool = True  # Auto-apply persona settings


class JobMatchUpdate(BaseModel):
    status: str
