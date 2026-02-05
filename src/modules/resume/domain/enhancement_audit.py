from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
import hashlib


class EnhancementType(str, Enum):
    """Types of enhancements - classified by truthfulness risk"""

    REPHRASE = "rephrase"  # Low risk - just better wording
    QUANTIFY_REQUEST = "quantify"  # Medium risk - asks user for metrics
    STRUCTURE = "structure"  # Low risk - reorganization
    KEYWORD_ALIGN = "keyword"  # Low risk - uses existing skills
    METRIC_SUGGESTION = "metric"  # HIGH RISK - must be verified


class EnhancementAuditLog(BaseModel):
    """Immutable audit log for AI enhancements - for GDPR and defensibility"""

    id: UUID
    user_id: UUID
    resume_id: UUID

    original_content: str
    enhanced_content: str
    final_content: str  # What user actually accepted

    enhancement_type: EnhancementType
    skills_referenced: List[str]
    metrics_verified_by_user: bool
    user_provided_values: Dict[str, str]  # Placeholder -> User value

    grounding_explanation: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Hash chain for immutability
    previous_hash: str
    content_hash: str = ""

    def compute_hash(self) -> str:
        content = f"{self.original_content}{self.enhanced_content}{self.previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()
