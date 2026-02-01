from enum import StrEnum


class DataClassification(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # PII and sensitive data


class RetentionPolicy(StrEnum):
    TRANSIENT = "transient"  # Delete after use
    SHORT_TERM = "short_term"  # 1 year
    LONG_TERM = "long_term"  # 5 years
    PERMANENT = "permanent"  # Until account deletion
