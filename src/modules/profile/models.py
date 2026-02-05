import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel
from src.core.security.encryption import EncryptedString


class UserProfile(BaseModel):
    """
    Comprehensive user profile replacing the legacy Persona.
    Stores encrypt personal info and structured preferences.
    """

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Personal Information (Encrypted)
    # Stored as a JSON string but encrypted at rest
    personal_info: Mapped[str] = mapped_column(
        EncryptedString, nullable=False, default="{}"
    )

    # Job Search Preferences
    search_preferences: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )

    # Agent Rules and Configuration
    agent_rules: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )

    # Common Application Answers (Encrypted)
    # Contains sensitive QA pairs
    application_answers: Mapped[str] = mapped_column(
        EncryptedString, nullable=False, default="{}"
    )

    # Resume Strategy
    resume_strategy: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )

    # Extended Profile Sections (Encrypted for Privacy)
    experience: Mapped[str] = mapped_column(
        EncryptedString, nullable=False, default="[]"
    )
    education: Mapped[str] = mapped_column(
        EncryptedString, nullable=False, default="[]"
    )
    skills: Mapped[str] = mapped_column(EncryptedString, nullable=False, default="[]")
    languages: Mapped[str] = mapped_column(
        EncryptedString, nullable=False, default="[]"
    )
    certifications: Mapped[str] = mapped_column(
        EncryptedString, nullable=False, default="[]"
    )

    # Vector Embedding for Semantic Search
    embedding: Mapped[Vector] = mapped_column(Vector(768), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
        onupdate="now()",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "src.modules.identity.domain.models.User", back_populates="profile"
    )

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"
