"""
Billing domain models for usage tracking and application-based billing.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel


class UsageRecord(BaseModel):
    """
    Tracks monthly usage per user for billing purposes.
    One record per user per billing period (month).
    """

    __tablename__ = "billing_usage_records"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Billing period (YYYY-MM format stored as string for simple queries)
    billing_period: Mapped[str] = mapped_column(
        String(7), nullable=False
    )  # e.g. "2026-02"

    # Application counts
    applications_submitted: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    agent_applications: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    manual_applications: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # AI usage
    ai_calls_made: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resumes_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cover_letters_generated: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    # Cost tracking (internal, for future metered billing)
    estimated_cost_usd: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )

    # Period boundaries
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        Index(
            "ix_usage_user_period",
            "user_id",
            "billing_period",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<UsageRecord(user_id={self.user_id}, "
            f"period={self.billing_period}, "
            f"apps={self.applications_submitted})>"
        )
