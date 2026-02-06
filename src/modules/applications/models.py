import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel

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
        nullable=True,  # Assuming cover_letter table exists or will be added
    )

    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    excitement_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    next_follow_up: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    job: Mapped["Job | None"] = relationship("Job")
    resume: Mapped["Resume | None"] = relationship("Resume")
    events: Mapped[list["ApplicationEvent"]] = relationship(
        "ApplicationEvent", back_populates="application", cascade="all, delete-orphan"
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
