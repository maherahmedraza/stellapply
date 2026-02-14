import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel
from src.core.security.encryption import EncryptedString

if TYPE_CHECKING:
    from src.modules.identity.domain.models import User
    from src.modules.job_search.domain.models import Job
    from src.modules.resume.domain.models import Resume


class ApplicationStatus(StrEnum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"


class Application(BaseModel):
    """
    Job application tracking model.
    Stores everything the agent does during the application process.
    """

    __tablename__ = "applications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True
    )

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.WISHLIST, nullable=False
    )

    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(
        String(3), default="EUR", nullable=False
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    resume_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True
    )
    cover_letter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    excitement_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    next_follow_up: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # --- Agent-specific fields ---

    # Match score at time of application (snapshot from JobMatcher)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # MinIO paths to agent-generated documents
    generated_cv_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    generated_cover_letter_url: Mapped[str | None] = mapped_column(
        String(1024), nullable=True
    )

    # Email used for this application (may differ from login email)
    application_email: Mapped[str | None] = mapped_column(
        EncryptedString, nullable=True
    )

    # Link back to the agent session that created this application
    agent_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # Whether this application was created by the agent (vs manually by user)
    is_agent_applied: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    job: Mapped["Job | None"] = relationship("Job")
    resume: Mapped["Resume | None"] = relationship("Resume")
    events: Mapped[list["ApplicationEvent"]] = relationship(
        "ApplicationEvent", back_populates="application", cascade="all, delete-orphan"
    )
    credentials: Mapped[list["ApplicationCredential"]] = relationship(
        "ApplicationCredential",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    form_data: Mapped[list["ApplicationFormData"]] = relationship(
        "ApplicationFormData",
        back_populates="application",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_applications_user_status", "user_id", "status"),
        Index(
            "ix_applications_user_created_at_desc",
            "user_id",
            "created_at",
            postgresql_using="btree",
            postgresql_ops={"created_at": "desc"},
        ),
        Index("ix_applications_user_next_follow_up", "user_id", "next_follow_up"),
        Index("ix_applications_agent_session", "agent_session_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<Application(id={self.id}, company={self.company_name}, "
            f"title={self.job_title}, status={self.status})>"
        )


class ApplicationEvent(BaseModel):
    """
    Append-only history of application status changes and events.
    """

    __tablename__ = "application_events"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    application: Mapped["Application"] = relationship(
        "Application", back_populates="events"
    )

    def __repr__(self) -> str:
        return (
            f"<ApplicationEvent(id={self.id}, application_id={self.application_id}, "
            f"to_status={self.to_status})>"
        )


class ApplicationCredential(BaseModel):
    """
    Encrypted credentials for portal accounts created by the agent during application.
    Stores login details so users can access their accounts later.
    All sensitive fields are encrypted at rest via EncryptedString.
    """

    __tablename__ = "application_credentials"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Portal identification
    portal_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    portal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Encrypted credentials
    email_used: Mapped[str] = mapped_column(EncryptedString, nullable=False)
    password: Mapped[str] = mapped_column(EncryptedString, nullable=False)

    # Account metadata
    account_created: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    login_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Relationships
    application: Mapped["Application"] = relationship(
        "Application", back_populates="credentials"
    )

    def __repr__(self) -> str:
        return (
            f"<ApplicationCredential(id={self.id}, portal={self.portal_name}, "
            f"application_id={self.application_id})>"
        )


class ApplicationFormData(BaseModel):
    """
    Snapshot of all data the agent entered in application forms.
    Serves as an audit trail for truth-grounded applications.
    Each record = one page of a multi-page application form.
    """

    __tablename__ = "application_form_data"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Which page of the form (for multi-page applications)
    page_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    page_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Form fields as structured JSON:
    # [{"field_name": "First Name", "field_type": "text", "value_entered": "John",
    #   "source_persona_field": "personal_info.first_name"}]
    form_fields: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, default=[], nullable=False
    )

    # Screenshot of the filled form (MinIO path)
    screenshot_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Whether this page was successfully submitted
    submitted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    application: Mapped["Application"] = relationship(
        "Application", back_populates="form_data"
    )

    def __repr__(self) -> str:
        return (
            f"<ApplicationFormData(id={self.id}, page={self.page_number}, "
            f"application_id={self.application_id})>"
        )
