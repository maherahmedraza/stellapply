import unittest.mock
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from src.modules.auto_apply.domain.models import ApplicationQueueItem, QueueStatus
from src.modules.auto_apply.domain.queue_manager import (
    QueueManager,
    RateLimitExceededError,
)
from src.modules.auto_apply.domain.repository import ApplicationQueueRepository
from src.modules.identity.domain.models import SubscriptionTier


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=ApplicationQueueRepository)


@pytest.fixture
def mock_redis():
    mock = AsyncMock(spec=Redis)
    mock.get.return_value = None  # Default: no limit hit
    return mock


@pytest.fixture
def queue_manager(mock_repo, mock_redis):
    return QueueManager(mock_repo, mock_redis)


@pytest.mark.asyncio
async def test_add_to_queue_free_tier(queue_manager):
    # Free tier should be blocked strictly as per implementation
    with pytest.raises(RateLimitExceededError, match="Free tier"):
        await queue_manager.add_to_queue(
            user_id=uuid4(),
            job_id=uuid4(),
            resume_id=uuid4(),
            cover_letter_id=uuid4(),
            user_tier=SubscriptionTier.FREE,
        )


@pytest.mark.asyncio
async def test_add_to_queue_success(queue_manager, mock_redis, mock_repo):
    user_id = uuid4()

    async def get_side_effect(key):
        return "0"

    mock_redis.get.side_effect = get_side_effect

    mock_repo.create.return_value = ApplicationQueueItem(
        id=uuid4(),
        user_id=user_id,
        job_id=uuid4(),
        status=QueueStatus.SCHEDULED,
        created_at=datetime.now(UTC),
        resume_id=uuid4(),
        cover_letter_id=uuid4(),
        scheduled_time=datetime.now(UTC),
    )

    # Mock Celery task
    with unittest.mock.patch(
        "src.modules.auto_apply.domain.queue_manager.apply_job_task"
    ) as mock_task:
        item = await queue_manager.add_to_queue(
            user_id=user_id,
            job_id=uuid4(),
            resume_id=uuid4(),
            cover_letter_id=uuid4(),
            user_tier=SubscriptionTier.PLUS,
        )

        assert item.status == QueueStatus.SCHEDULED
        mock_repo.create.assert_called_once()
        assert mock_redis.get.call_count == 2
        mock_task.apply_async.assert_called_once()


@pytest.mark.asyncio
async def test_rate_limit_daily_exceeded(queue_manager, mock_redis):
    # Fix AsyncMock return for failure case
    async def get_limit_exceeded(key):
        return "5"

    mock_redis.get.side_effect = get_limit_exceeded

    with pytest.raises(RateLimitExceededError, match="Daily application limit"):
        await queue_manager.add_to_queue(
            user_id=uuid4(),
            job_id=uuid4(),
            resume_id=uuid4(),
            cover_letter_id=uuid4(),
            user_tier=SubscriptionTier.PLUS,
        )


@pytest.mark.asyncio
async def test_calculate_optimal_time(queue_manager):
    scheduled = queue_manager._calculate_optimal_time(None, None)
    assert scheduled > datetime.now(UTC)
    # Basic sanity check that it returns a datetime in future
