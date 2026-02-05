import asyncio
import functools
import logging
from datetime import UTC, datetime
from typing import Any, Callable, TypeVar
from uuid import UUID

from celery import shared_task
from src.core.database.connection import get_db_context
from src.modules.auto_apply.domain.models import QueueStatus
from src.modules.auto_apply.domain.repository import ApplicationQueueRepository
from src.modules.auto_apply.infrastructure.browser.form_filler import ApplicationResult

logger = logging.getLogger(__name__)

T = TypeVar("T")


def async_to_sync(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to run an async function in a synchronous context.
    Properly manages event loops for Celery workers.
    """

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If already running (not typical for Celery but possible),
            # we need a different strategy like running in a separate thread
            return asyncio.run_coroutine_threadsafe(f(*args, **kwargs), loop).result()
        else:
            return loop.run_until_complete(f(*args, **kwargs))

    return wrapper


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    retry_backoff=True,
    name="src.workers.tasks.auto_apply.apply_job_task",
)
@async_to_sync
async def apply_job_task(self, queue_item_id: str):
    """
    Process a single job application.
    Bridged to async execution via decorator.
    """
    async with get_db_context() as session:
        repo = ApplicationQueueRepository(session)

        queue_item = await repo.get(UUID(queue_item_id))
        if not queue_item:
            logger.error(f"Queue item {queue_item_id} not found")
            return "Item not found"

        if queue_item.status == QueueStatus.CANCELLED:
            return "Cancelled"

        # Update to IN_PROGRESS
        queue_item.status = QueueStatus.IN_PROGRESS
        queue_item.last_attempt_at = datetime.now(UTC)
        queue_item.attempt_count += 1
        await repo.update(queue_item)
        await session.commit()

        try:
            # Placeholder for actual browser execution
            result = ApplicationResult(
                success=True, filled_fields=[], errors=[], pages_processed=1
            )

            if result.success:
                queue_item.status = QueueStatus.COMPLETED
                queue_item.screenshot_path = "path/to/screenshot.png"
            else:
                error_msg = f"Application failed: {result.errors}"
                queue_item.last_error = error_msg
                queue_item.status = QueueStatus.FAILED

            await repo.update(queue_item)
            await session.commit()

        except Exception as e:
            logger.error(f"Error processing job application: {e}", exc_info=True)
            queue_item.last_error = str(e)
            queue_item.status = QueueStatus.FAILED
            await repo.update(queue_item)

            # Use self.retry if retryable, otherwise re-raise
            if self.request.retries < self.max_retries:
                await session.commit()
                raise self.retry(exc=e)

            await session.commit()
            raise e

        return str(queue_item.status)
