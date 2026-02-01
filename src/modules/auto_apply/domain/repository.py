from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auto_apply.domain.models import (
    ApplicationQueue,
    ApplicationQueueItem,
    QueueStatus,
)


class ApplicationQueueRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(
        self, user_id: UUID, status: QueueStatus | None = None
    ) -> Sequence[ApplicationQueueItem]:
        stmt = select(ApplicationQueue).where(ApplicationQueue.user_id == user_id)
        if status:
            stmt = stmt.where(ApplicationQueue.status == status.value)

        result = await self.session.execute(stmt)
        return [r.to_pydantic() for r in result.scalars().all()]

    async def create(self, item: ApplicationQueueItem) -> ApplicationQueueItem:
        db_item = ApplicationQueue(
            id=item.id,
            user_id=item.user_id,
            job_id=item.job_id,
            priority=item.priority,
            status=item.status.value,
            scheduled_time=item.scheduled_time,
            resume_id=item.resume_id,
            cover_letter_id=item.cover_letter_id,
            attempt_count=item.attempt_count,
            max_attempts=item.max_attempts,
            created_at=item.created_at,
        )
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item.to_pydantic()

    async def update(self, item: ApplicationQueueItem) -> ApplicationQueueItem:
        stmt = (
            update(ApplicationQueue)
            .where(ApplicationQueue.id == item.id)
            .values(
                status=item.status.value,
                attempt_count=item.attempt_count,
                last_attempt_at=item.last_attempt_at,
                last_error=item.last_error,
                screenshot_path=item.screenshot_path,
                scheduled_time=item.scheduled_time,
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return item

    async def get(self, id: UUID) -> ApplicationQueueItem | None:
        stmt = select(ApplicationQueue).where(ApplicationQueue.id == id)
        result = await self.session.execute(stmt)
        db_item = result.scalar_one_or_none()
        return db_item.to_pydantic() if db_item else None

    async def update_status_bulk(
        self, user_id: UUID, from_status: QueueStatus, to_status: QueueStatus
    ) -> int:
        stmt = (
            update(ApplicationQueue)
            .where(
                ApplicationQueue.user_id == user_id,
                ApplicationQueue.status == from_status.value,
            )
            .values(status=to_status.value)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
