from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class EnhancementType(str, Enum):
    """Types of allowed enhancements"""

    REWORD = "reword"  # Change wording, keep meaning
    RESTRUCTURE = "restructure"  # Reorganize for clarity
    QUANTIFY = "quantify"  # Add metrics (requires confirmation)
    ACTION_VERB = "action_verb"  # Replace weak verbs with strong ones
    KEYWORD_INJECT = "keyword"  # Add relevant keywords from existing skills
    CONDENSE = "condense"  # Make more concise
    EXPAND = "expand"  # Add detail from persona (verified)


class VerificationStatus(str, Enum):
    """Status of truth verification"""

    VERIFIED = "verified"  # Matches persona exactly
    PLAUSIBLE = "plausible"  # Reasonable inference from persona
    NEEDS_CONFIRMATION = "needs_confirmation"  # User must confirm
    REJECTED = "rejected"  # Cannot be verified, rejected


class EnhancementSuggestionSchema(BaseModel):
    """A single enhancement suggestion with truth verification"""

    original_text: str
    enhanced_text: str
    enhancement_type: EnhancementType
    verification_status: VerificationStatus
    confidence_score: float = Field(ge=0.0, le=1.0)

    # Truth grounding evidence
    source_persona_fields: List[str] = []
    verification_notes: str = ""

    # For QUANTIFY type - requires user confirmation
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None

    # What changed
    changes_made: List[str] = []

    # Risk assessment
    defensibility_score: float = Field(ge=0.0, le=1.0, default=1.0)
    interview_talking_points: List[str] = []


class EnhancementRequest(BaseModel):
    """Request for truth-grounded enhancement"""

    original_content: str
    content_type: str  # "bullet_point", "summary", "description"
    target_job_keywords: Optional[List[str]] = None


class EnhancementResponse(BaseModel):
    """Response containing multiple enhancement options"""

    enhancements: List[EnhancementSuggestionSchema]


class MetricConfirmationRequest(BaseModel):
    """Request to confirm metrics in a suggestion"""

    confirmation_id: str
    user_responses: Dict[str, str]


class VerificationContextResponse(BaseModel):
    """Context extracted from Persona for verification"""

    verified_skills: List[str]
    verified_tools: List[str]
    verified_companies: List[str]
    verified_job_titles: List[str]
    years_of_experience: Dict[str, float]
    certifications: List[str]
    education: List[Dict[str, str]]
    achievements_count: int
