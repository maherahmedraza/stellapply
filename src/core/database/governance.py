"""
Data Governance Framework for GDPR/DSGVO Compliance.

This module provides data classification, retention policies,
and governance metadata for German data protection requirements.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DataClassification(StrEnum):
    """Data classification levels for GDPR compliance."""

    PUBLIC = "public"  # No restrictions
    INTERNAL = "internal"  # Standard protection
    CONFIDENTIAL = "confidential"  # Encrypted, logged access
    RESTRICTED = "restricted"  # PII and sensitive data - encrypted + audited


class RetentionPolicy(StrEnum):
    """Data retention policies per German law requirements."""

    TRANSIENT = "transient"  # Delete after use
    SHORT_TERM = "short_term"  # 1 year
    MEDIUM_TERM = "medium_term"  # 3 years
    LONG_TERM = "long_term"  # 5 years
    LEGAL_MINIMUM = "legal_minimum"  # 6 years (HGB § 257)
    TAX_RECORDS = "tax_records"  # 10 years (AO § 147)
    PERMANENT = "permanent"  # Until account deletion
    PERMANENT_ANONYMIZED = "permanent_anonymized"  # Anonymized for analytics


class DataCategory(StrEnum):
    """GDPR data categories for processing records."""

    PII_CRITICAL = "pii_critical"  # Name, email, phone, ID - encrypted + hashed
    PII_STANDARD = "pii_standard"  # Address, work history - encrypted
    SENSITIVE = "sensitive"  # Art. 9: health, ethnic, political - special protection
    BEHAVIORAL = "behavioral"  # Usage patterns, preferences
    TECHNICAL = "technical"  # IP, device info - hashed
    FINANCIAL = "financial"  # Payment data, salary - encrypted + PCI-DSS


class LegalBasisCode(StrEnum):
    """GDPR Article 6 legal basis codes."""

    CONSENT = "6.1.a"  # Consent given
    CONTRACT = "6.1.b"  # Necessary for contract
    LEGAL_OBLIGATION = "6.1.c"  # Legal requirement
    VITAL_INTERESTS = "6.1.d"  # Protect vital interests
    PUBLIC_TASK = "6.1.e"  # Public interest task
    LEGITIMATE_INTERESTS = "6.1.f"  # Legitimate business interests


class DataGovernanceMetadata(BaseModel):
    """
    Metadata for data governance and GDPR compliance.

    Attach this to data models to track processing requirements.
    """

    classification: DataClassification
    category: DataCategory
    retention_policy: RetentionPolicy
    legal_basis: LegalBasisCode
    purpose: list[str] = Field(
        default_factory=list,
        description="Processing purposes (e.g., 'job_matching', 'resume_generation')",
    )

    # Data controller information
    data_controller: str = "StellarApply GmbH"
    processing_location: str = "EU"

    # Third-party sharing
    third_party_recipients: list[str] = Field(default_factory=list)
    requires_consent: bool = True

    # Encryption and anonymization
    encryption_required: bool = True
    anonymization_method: str | None = None

    # Audit requirements
    access_logging: bool = True
    modification_tracking: bool = True

    # Timestamps
    created_at: datetime | None = None
    last_reviewed_at: datetime | None = None


# Pre-defined governance profiles for common data types
GOVERNANCE_PROFILES: dict[str, DataGovernanceMetadata] = {
    "pii_critical": DataGovernanceMetadata(
        classification=DataClassification.RESTRICTED,
        category=DataCategory.PII_CRITICAL,
        retention_policy=RetentionPolicy.PERMANENT,
        legal_basis=LegalBasisCode.CONTRACT,
        purpose=["user_identification", "communication"],
        encryption_required=True,
        access_logging=True,
    ),
    "resume_content": DataGovernanceMetadata(
        classification=DataClassification.CONFIDENTIAL,
        category=DataCategory.PII_STANDARD,
        retention_policy=RetentionPolicy.PERMANENT,
        legal_basis=LegalBasisCode.CONTRACT,
        purpose=["resume_generation", "job_application"],
        encryption_required=True,
        third_party_recipients=["Job Board APIs"],
    ),
    "ai_analysis": DataGovernanceMetadata(
        classification=DataClassification.CONFIDENTIAL,
        category=DataCategory.BEHAVIORAL,
        retention_policy=RetentionPolicy.MEDIUM_TERM,
        legal_basis=LegalBasisCode.CONSENT,
        purpose=["job_matching", "skill_analysis"],
        requires_consent=True,
        third_party_recipients=["Google Gemini API"],
    ),
    "analytics": DataGovernanceMetadata(
        classification=DataClassification.INTERNAL,
        category=DataCategory.BEHAVIORAL,
        retention_policy=RetentionPolicy.PERMANENT_ANONYMIZED,
        legal_basis=LegalBasisCode.LEGITIMATE_INTERESTS,
        purpose=["service_improvement", "usage_analytics"],
        anonymization_method="k-anonymity",
        encryption_required=False,
    ),
}
