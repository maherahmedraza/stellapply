import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel


class Job(BaseModel):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )
    source: Mapped[str | None] = mapped_column(String(100), index=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(255), index=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_embedding: Mapped[Any | None] = mapped_column(
        Vector(768)
    )  # Gemini 768-dim

    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    salary_currency: Mapped[str | None] = mapped_column(String(10))

    job_type: Mapped[str | None] = mapped_column(
        String(50)
    )  # full-time, contract, etc.
    work_setting: Mapped[str | None] = mapped_column(
        String(50)
    )  # remote, hybrid, on-site

    raw_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})

    status: Mapped[str] = mapped_column(String(50), default="active", index=True)

    posted_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    expired_at: Mapped[datetime | None] = mapped_column(DateTime)


class JobMatch(BaseModel):
    __tablename__ = "job_matches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True
    )

    overall_score: Mapped[int] = mapped_column(nullable=False, index=True)
    vector_score: Mapped[float | None] = mapped_column(Float)

    # Granular AI analysis
    analysis: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})

    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, reviewed, applied, rejected

    # Relationships
    job = relationship("Job", backref="matches")
