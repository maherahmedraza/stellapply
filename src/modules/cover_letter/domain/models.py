import uuid
from enum import StrEnum
from typing import Any

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel


class Tone(StrEnum):
    PROFESSIONAL = "PROFESSIONAL"
    CONVERSATIONAL = "CONVERSATIONAL"
    ENTHUSIASTIC = "ENTHUSIASTIC"


class Length(StrEnum):
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    COMPREHENSIVE = "COMPREHENSIVE"


class Emphasis(StrEnum):
    SKILLS = "SKILLS"
    CULTURE = "CULTURE"
    ACHIEVEMENTS = "ACHIEVEMENTS"


class CoverLetter(BaseModel):
    """Container for a generated cover letter."""

    __tablename__ = "cover_letters"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True
    )
    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
    quality_metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})

    # Relationships
    versions: Mapped[list["CoverLetterVersion"]] = relationship(
        "CoverLetterVersion",
        back_populates="cover_letter",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CoverLetter(user_id={self.user_id}, job_id={self.job_id})>"


class CoverLetterVersion(BaseModel):
    """Historical versions and A/B test tracking."""

    __tablename__ = "cover_letter_versions"

    cover_letter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cover_letters.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_id: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # For A/B testing
    change_summary: Mapped[str | None] = mapped_column(Text)

    cover_letter: Mapped[CoverLetter] = relationship(
        "CoverLetter", back_populates="versions"
    )

    def __repr__(self) -> str:
        return (
            f"<CoverLetterVersion(letter_id={self.cover_letter_id}, "
            f"prompt={self.prompt_id})>"
        )
