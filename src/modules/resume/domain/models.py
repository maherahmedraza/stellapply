import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base_model import BaseModel


class Resume(BaseModel):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_id: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
    pdf_url: Mapped[str | None] = mapped_column(String(512))
    docx_url: Mapped[str | None] = mapped_column(String(512))
    ats_score: Mapped[int | None] = mapped_column(Integer)
    analysis_results: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)


class ResumeTemplate(BaseModel):
    __tablename__ = "resume_templates"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    schema: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
