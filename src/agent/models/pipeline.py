from datetime import datetime
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchSource(BaseModel):
    platform: str
    url: str | None = None
    search_query: str | None = None


class FilterConfig(BaseModel):
    min_match_score: float = 0.6
    max_match_score: float = 1.0
    exclude_companies: List[str] = Field(default_factory=list)
    exclude_keywords: List[str] = Field(default_factory=list)
    location_filter: str | None = None
    remote_only: bool = False
    job_types: List[str] = Field(default_factory=list)


class PipelineConfig(BaseModel):
    search_sources: List[SearchSource]
    max_applications: int = 10
    require_approval: bool = True
    filters: FilterConfig = Field(default_factory=FilterConfig)
    resume_file_path: str | None = None


class DiscoveredJob(BaseModel):
    title: str
    company: str
    url: str
    location: str | None = None
    salary_range: str | None = None
    description_snippet: str
    source_platform: str
    discovered_at: datetime = Field(default_factory=datetime.now)


class ScoredJob(DiscoveredJob):
    match_score: float
    match_reasons: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)


class ApplicationAttempt(BaseModel):
    job: ScoredJob
    status: str  # 'success', 'failed', 'skipped_by_user', 'registration_failed', 'captcha_blocked'
    error: str | None = None
    confirmation_screenshot: bytes | None = None
    fields_filled: Dict[str, Any] | None = None
    started_at: datetime
    completed_at: datetime
    duration_seconds: float


class PipelineResult(BaseModel):
    session_id: UUID
    total_discovered: int
    total_matched: int
    total_applied: int
    total_failed: int
    total_skipped: int
    attempts: List[ApplicationAttempt]
    started_at: datetime
    completed_at: datetime


class PipelineState(BaseModel):
    session_id: UUID
    stage: (
        str  # 'discovering', 'filtering', 'applying', 'completed', 'paused', 'failed'
    )
    current_job_index: int = 0
    total_jobs: int = 0
    current_action: str = ""
    progress_percentage: float = 0.0
    errors: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
