from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field


class AgentType(StrEnum):
    SCOUT = "scout"
    APPLICANT = "applicant"
    REGISTRAR = "registrar"


class AgentStatus(StrEnum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTaskCreate(BaseModel):
    type: AgentType
    priority: TaskPriority = TaskPriority.MEDIUM
    payload: dict[str, Any]
    user_id: uuid.UUID


class AgentTaskResponse(BaseModel):
    id: uuid.UUID
    type: AgentType
    status: TaskStatus
    priority: TaskPriority
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class AgentState(BaseModel):
    id: str  # Worker ID
    status: AgentStatus
    current_task_id: uuid.UUID | None = None
    capabilities: list[AgentType]
    last_heartbeat: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserSession(BaseModel):
    id: str
    context_id: str
    user_id: uuid.UUID
    active_page_url: str | None = None
    cookies_count: int = 0
    created_at: datetime
    last_accessed: datetime
