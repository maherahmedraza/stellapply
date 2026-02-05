import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base_model import BaseModel
from src.agent.models.schemas import AgentType, TaskPriority, TaskStatus


class AgentTask(BaseModel):
    """
    Database model for persistent agent tasks.
    """

    __tablename__ = "agent_tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    type: Mapped[AgentType] = mapped_column(Enum(AgentType), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False
    )

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Execution metadata
    worker_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    retries: Mapped[int] = mapped_column(default=0, nullable=False)

    __table_args__ = (
        Index("ix_agent_tasks_status_priority", "status", "priority"),
        Index("ix_agent_tasks_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AgentTask(id={self.id}, type={self.type}, status={self.status})>"
