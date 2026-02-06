import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import BYTEA, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel

if TYPE_CHECKING:
    from src.modules.resume.domain.models import Resume
    from src.modules.profile.models import UserProfile


from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLAlchemyEnum


class SubscriptionTier(str, PyEnum):
    FREE = "free"
    PLUS = "plus"
    PRO = "pro"
    PREMIUM = "premium"


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email_encrypted: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    email_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    tier: Mapped[SubscriptionTier] = mapped_column(
        SQLAlchemyEnum(SubscriptionTier, name="subscription_tier"),
        default=SubscriptionTier.FREE,
        nullable=False,
    )
    governance_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})

    resumes: Mapped[list["Resume"]] = relationship("Resume", back_populates="user")
    settings: Mapped["UserSettings | None"] = relationship(
        "UserSettings", back_populates="user", uselist=False
    )
    profile: Mapped["UserProfile | None"] = relationship(
        "src.modules.profile.models.UserProfile", back_populates="user", uselist=False
    )

    @property
    def email(self) -> str:
        """Decrypts and returns the user email."""
        from src.core.security.encryption import decrypt_data

        # Decode BYTEA to string before decryption if stored as bytes
        enc_data = self.email_encrypted
        if isinstance(enc_data, bytes):
            enc_data = enc_data.decode()
        return decrypt_data(enc_data)

    @email.setter
    def email(self, value: str) -> None:
        """Encrypts and sets the user email."""
        from src.core.security.encryption import encrypt_data

        self.email_encrypted = encrypt_data(value).encode()


class UserSettings(BaseModel):
    """User preferences and settings"""

    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )

    # Display preferences
    theme: Mapped[str] = mapped_column(String(20), default="system")
    language: Mapped[str] = mapped_column(String(10), default="en")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    date_format: Mapped[str] = mapped_column(String(20), default="YYYY-MM-DD")

    # Notification preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    job_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    weekly_digest: Mapped[bool] = mapped_column(Boolean, default=True)
    quiet_hours_start: Mapped[str | None] = mapped_column(String(5), nullable=True)
    quiet_hours_end: Mapped[str | None] = mapped_column(String(5), nullable=True)

    # Job search preferences
    match_threshold: Mapped[int] = mapped_column(Integer, default=70)
    preferred_work_type: Mapped[str] = mapped_column(String(20), default="any")
    salary_visible: Mapped[bool] = mapped_column(Boolean, default=False)

    # Automation preferences
    auto_apply_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_apply_limit: Mapped[int] = mapped_column(Integer, default=5)
    auto_apply_min_match: Mapped[int] = mapped_column(Integer, default=85)

    user: Mapped["User"] = relationship("User", back_populates="settings")
