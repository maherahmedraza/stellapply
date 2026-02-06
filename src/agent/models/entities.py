import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Float, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel
from src.modules.applications.models import ApplicationStatus

if TYPE_CHECKING:
    from src.modules.identity.domain.models import User


class AgentSession(BaseModel):
    __tablename__ = "agent_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    state: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="queued", nullable=False
    )  # queued, running, paused, completed, failed, cancelled

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    discovered_jobs: Mapped[List["DiscoveredJob"]] = relationship(
        "DiscoveredJob", back_populates="session", cascade="all, delete-orphan"
    )
    application_attempts: Mapped[List["ApplicationAttemptEntity"]] = relationship(
        "ApplicationAttemptEntity",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class DiscoveredJob(BaseModel):
    __tablename__ = "discovered_jobs"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_sessions.id"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    description_snippet: Mapped[Optional[str]] = mapped_column(Text)

    match_score: Mapped[Optional[float]] = mapped_column(Float)
    match_reasons: Mapped[list] = mapped_column(JSONB, default=[])

    status: Mapped[str] = mapped_column(
        String(20), default="discovered"
    )  # discovered, matched, approved, applied, skipped, failed

    source_platform: Mapped[str] = mapped_column(String(50))

    session: Mapped["AgentSession"] = relationship(
        "AgentSession", back_populates="discovered_jobs"
    )
    attempts: Mapped[List["ApplicationAttemptEntity"]] = relationship(
        "ApplicationAttemptEntity", back_populates="discovered_job"
    )

    __table_args__ = (
        Index("ix_discovered_jobs_session_status", "session_id", "status"),
    )


class ApplicationAttemptEntity(BaseModel):
    __tablename__ = "application_attempts"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_sessions.id"), nullable=False
    )
    discovered_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("discovered_jobs.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    status: Mapped[str] = mapped_column(String(50), nullable=False)
    # success, failed, captcha, registration_failed, skipped

    fields_submitted: Mapped[dict] = mapped_column(JSONB, nullable=True)
    confirmation_screenshot_path: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)

    session: Mapped["AgentSession"] = relationship(
        "AgentSession", back_populates="application_attempts"
    )
    discovered_job: Mapped["DiscoveredJob"] = relationship(
        "DiscoveredJob", back_populates="attempts"
    )


class AgentIntervention(BaseModel):
    __tablename__ = "agent_interventions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_sessions.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    type: Mapped[str] = mapped_column(String(50), nullable=False)
    # captcha, unknown_question, approval_gate, login_2fa, assessment, ambiguous_choice, error_recovery, custom

    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    # pending, responded, expired, skipped

    context: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # url, screenshot_b64, question, etc.

    response: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # action, value, instruction

    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    session: Mapped["AgentSession"] = relationship("AgentSession")
    # user relationship is likely defined in User model or we assume implicit
