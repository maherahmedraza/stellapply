"""
GDPR/DSGVO Consent and Data Subject Rights Models.

German Data Protection Law (DSGVO) Compliance:
- Article 6: Lawfulness of processing
- Article 7: Conditions for consent
- Article 15-22: Data subject rights
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel as PydanticModel
from pydantic import Field
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base_model import BaseModel


class ConsentPurpose(StrEnum):
    """GDPR consent purposes as per Article 6."""

    ESSENTIAL = "essential"  # Required for service operation
    ANALYTICS = "analytics"  # Usage analytics and improvements
    MARKETING = "marketing"  # Marketing communications
    AI_PROFILING = "ai_profiling"  # AI-based job matching profiling
    THIRD_PARTY_SHARING = "third_party_sharing"  # Data sharing with partners
    AUTOMATED_DECISIONS = "automated_decisions"  # Auto-apply automation


class LegalBasis(StrEnum):
    """GDPR Article 6 legal basis for processing."""

    CONSENT = "consent"  # Art. 6(1)(a)
    CONTRACT = "contract"  # Art. 6(1)(b)
    LEGAL_OBLIGATION = "legal_obligation"  # Art. 6(1)(c)
    VITAL_INTERESTS = "vital_interests"  # Art. 6(1)(d)
    PUBLIC_TASK = "public_task"  # Art. 6(1)(e)
    LEGITIMATE_INTERESTS = "legitimate_interests"  # Art. 6(1)(f)


class DataCategory(StrEnum):
    """Data classification for GDPR compliance."""

    PII_CRITICAL = "pii_critical"  # Name, email, phone - encrypted + hashed
    PII_STANDARD = "pii_standard"  # Address, work history - encrypted
    SENSITIVE = "sensitive"  # Salary expectations, health info - encrypted + logged
    INTERNAL = "internal"  # Preferences, settings - standard protection
    PUBLIC = "public"  # No restrictions


class RetentionPeriod(StrEnum):
    """Data retention policies."""

    ACTIVE_ACCOUNT = "active_account"  # Retained while account is active
    POST_DELETION_30D = "30_days"  # 30 days after account deletion
    POST_DELETION_90D = "90_days"  # 90 days (legal requirements)
    LEGAL_MINIMUM_6Y = "6_years"  # German HGB § 257 (business records)
    PERMANENT_ANONYMIZED = "permanent_anonymized"  # Anonymized for analytics


class ConsentRecord(BaseModel):
    """
    Tracks user consent for specific purposes.
    GDPR Article 7: Conditions for consent.
    """

    __tablename__ = "consent_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    purpose: Mapped[ConsentPurpose] = mapped_column(
        Enum(ConsentPurpose), nullable=False, index=True
    )
    legal_basis: Mapped[LegalBasis] = mapped_column(
        Enum(LegalBasis), nullable=False, default=LegalBasis.CONSENT
    )

    is_granted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Version tracking for consent updates
    consent_version: Mapped[str] = mapped_column(String(20), nullable=False)
    policy_version: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # Privacy policy version

    # Audit fields
    ip_address_hash: Mapped[str | None] = mapped_column(
        String(64)
    )  # Hashed for privacy
    user_agent_hash: Mapped[str | None] = mapped_column(String(64))

    # Additional metadata
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    def __repr__(self) -> str:
        return (
            f"<ConsentRecord(user_id={self.user_id}, purpose={self.purpose}, "
            f"granted={self.is_granted})>"
        )


class DataProcessingRecord(BaseModel):
    """
    Records of Lawful Data Processing Activities.
    GDPR Article 30: Records of processing activities.
    """

    __tablename__ = "data_processing_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    activity_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "resume_generation"
    data_categories: Mapped[list[str]] = mapped_column(
        JSONB, default=[]
    )  # ["pii_critical", "pii_standard"]
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    legal_basis: Mapped[LegalBasis] = mapped_column(Enum(LegalBasis), nullable=False)

    recipients: Mapped[list[str] | None] = mapped_column(
        JSONB
    )  # ["Gemini AI", "Job Board API"]
    retention_period: Mapped[RetentionPeriod] = mapped_column(
        Enum(RetentionPeriod), nullable=False
    )

    processing_location: Mapped[str] = mapped_column(
        String(50), default="EU", nullable=False
    )
    transfer_safeguards: Mapped[str | None] = mapped_column(
        Text
    )  # For non-EU transfers

    def __repr__(self) -> str:
        return f"<DataProcessingRecord(activity={self.activity_type}, user={self.user_id})>"


class DataSubjectRequest(BaseModel):
    """
    Data Subject Access Requests (DSAR) tracking.
    GDPR Articles 15-22: Data subject rights.
    """

    __tablename__ = "data_subject_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    request_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # access, erasure, portability, rectification, restriction
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending, processing, completed, rejected

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    deadline_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )  # 30 days by law
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Response details
    response_notes: Mapped[str | None] = mapped_column(Text)
    export_file_path: Mapped[str | None] = mapped_column(String(512))  # MinIO path

    # Verification
    identity_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_method: Mapped[str | None] = mapped_column(String(50))

    def __repr__(self) -> str:
        return (
            f"<DataSubjectRequest(type={self.request_type}, "
            f"status={self.status}, user={self.user_id})>"
        )


# Pydantic schemas for API
class ConsentGrantRequest(PydanticModel):
    """Request to grant consent for a specific purpose."""

    purpose: ConsentPurpose
    granted: bool


class ConsentStatusResponse(PydanticModel):
    """Current consent status for a user."""

    purpose: ConsentPurpose
    is_granted: bool
    granted_at: datetime | None = None
    consent_version: str
    can_withdraw: bool = True


class DataExportRequest(PydanticModel):
    """Request for data portability export."""

    format: str = Field(default="json", pattern="^(json|pdf|csv)$")
    include_audit_trail: bool = False


class ErasureRequest(PydanticModel):
    """Request for right to erasure."""

    confirm_deletion: bool
    keep_anonymized_analytics: bool = False
    reason: str | None = None
