from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field


class InterventionType(StrEnum):
    CAPTCHA = "captcha"
    UNKNOWN_QUESTION = "unknown_question"
    APPROVAL_GATE = "approval_gate"
    LOGIN_2FA = "login_2fa"
    ASSESSMENT = "assessment"
    AMBIGUOUS_CHOICE = "ambiguous_choice"
    ERROR_RECOVERY = "error_recovery"
    CUSTOM = "custom"


class InterventionStatus(StrEnum):
    PENDING = "pending"
    RESPONDED = "responded"
    EXPIRED = "expired"
    SKIPPED = "skipped"


class InterventionContext(BaseModel):
    """
    Context provided to the user to help them make a decision.
    """
    url: str
    page_title: str | None = None
    screenshot_b64: str | None = None
    question: str | None = None
    field_selector: str | None = None
    options: List[str] | None = None
    agent_thinking: str | None = None
    job_title: str | None = None
    company: str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InterventionResponse(BaseModel):
    """
    The user's response to the intervention.
    """
    action: str = Field(..., description="provide_answer, skip_field, solve_captcha, abort_application")
    value: str | None = Field(None, description="User's typed response or selected option")
    instruction: str | None = Field(None, description="Additional instruction for agent")


class AgentIntervention(BaseModel):
    """
    Model for API responses representing an intervention.
    """
    id: uuid.UUID
    session_id: uuid.UUID
    user_id: uuid.UUID
    type: InterventionType
    status: InterventionStatus
    context: InterventionContext
    response: InterventionResponse | None = None
    created_at: datetime
    responded_at: datetime | None = None
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateInterventionRequest(BaseModel):
    """
    Internal use: request to create an intervention.
    """
    type: InterventionType
    context: InterventionContext
