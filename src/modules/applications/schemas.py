import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.modules.applications.models import ApplicationStatus


class ApplicationEventResponse(BaseModel):
    id: uuid.UUID
    application_id: uuid.UUID
    from_status: str | None = None
    to_status: str
    notes: str | None = None
    created_at: datetime
    created_by: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class ApplicationBase(BaseModel):
    company_name: str = Field(..., max_length=255)
    job_title: str = Field(..., max_length=255)
    job_url: HttpUrl | None = None
    status: ApplicationStatus = ApplicationStatus.WISHLIST
    applied_at: datetime | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = Field("EUR", min_length=3, max_length=3)
    notes: str | None = None
    resume_id: uuid.UUID | None = None
    cover_letter_id: uuid.UUID | None = None
    source: str | None = Field(None, max_length=100)
    excitement_rating: int | None = Field(None, ge=1, le=5)
    next_follow_up: datetime | None = None
    job_id: uuid.UUID | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company_name: str | None = Field(None, max_length=255)
    job_title: str | None = Field(None, max_length=255)
    job_url: HttpUrl | None = None
    status: ApplicationStatus | None = None
    applied_at: datetime | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = Field(None, min_length=3, max_length=3)
    notes: str | None = None
    resume_id: uuid.UUID | None = None
    cover_letter_id: uuid.UUID | None = None
    source: str | None = Field(None, max_length=100)
    excitement_rating: int | None = Field(None, ge=1, le=5)
    next_follow_up: datetime | None = None
    job_id: uuid.UUID | None = None


class ApplicationResponse(ApplicationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    events: list[ApplicationEventResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    per_page: int

    model_config = ConfigDict(from_attributes=True)


class ApplicationStats(BaseModel):
    total: int
    by_status: dict[str, int]
    weekly_applied: int
    response_rate: float
    avg_time_to_response_days: float

    model_config = ConfigDict(from_attributes=True)


class BulkUpdateStatus(BaseModel):
    application_ids: list[uuid.UUID]
    new_status: ApplicationStatus
