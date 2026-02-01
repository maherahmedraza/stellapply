from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base_model import BaseModel as DBBaseModel


class QueueStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ApplicationQueueItem(BaseModel):
    id: UUID
    user_id: UUID
    job_id: UUID
    priority: int = 0
    status: QueueStatus
    scheduled_time: datetime | None
    attempt_count: int = 0
    max_attempts: int = 3
    created_at: datetime

    resume_id: UUID
    cover_letter_id: UUID

    last_attempt_at: datetime | None = None
    last_error: str | None = None
    screenshot_path: str | None = None


class ApplicationQueue(DBBaseModel):
    __tablename__ = "application_queue"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(
        String(20), default=QueueStatus.PENDING.value, index=True
    )
    priority: Mapped[int] = mapped_column(Integer, default=0)

    scheduled_time: Mapped[datetime | None] = mapped_column(DateTime, index=True)

    resume_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    cover_letter_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)

    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_error: Mapped[str | None] = mapped_column(String)
    screenshot_path: Mapped[str | None] = mapped_column(String)

    def to_pydantic(self) -> ApplicationQueueItem:
        return ApplicationQueueItem(
            id=self.id,
            user_id=self.user_id,
            job_id=self.job_id,
            priority=self.priority,
            status=QueueStatus(self.status),
            scheduled_time=self.scheduled_time,
            attempt_count=self.attempt_count,
            max_attempts=self.max_attempts,
            created_at=self.created_at,
            resume_id=self.resume_id,
            cover_letter_id=self.cover_letter_id,
            last_attempt_at=self.last_attempt_at,
            last_error=self.last_error,
            screenshot_path=self.screenshot_path,
        )
