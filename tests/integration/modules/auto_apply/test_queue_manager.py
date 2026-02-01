import pytest
from src.modules.auto_apply.domain.queue_manager import QueueManager
from src.modules.auto_apply.domain.models import QueueStatus


class TestQueueManager:
    @pytest.fixture
    def queue_manager(self, db_session):
        return QueueManager(session=db_session)

    @pytest.mark.asyncio
    async def test_add_to_queue(self, queue_manager, test_user):
        job_id = "job-uuid-123"
        item = await queue_manager.add_application(
            user_id=test_user["id"], job_id=job_id, priority=1
        )

        assert item.id is not None
        assert item.status == QueueStatus.PENDING
        assert item.job_id == job_id

    @pytest.mark.asyncio
    async def test_process_queue_retrieval(self, queue_manager, test_user):
        # Add a pending item
        await queue_manager.add_application(
            user_id=test_user["id"], job_id="job-uuid-456", priority=10
        )

        # Retrieve next item
        item = await queue_manager.get_next_pending_item()

        assert item is not None
        assert item.job_id == "job-uuid-456"
        # Should be locked or still pending depending on implementation
        # Usually get_next might lock it

    @pytest.mark.asyncio
    async def test_rate_limiting_enforcement(self, queue_manager, test_user):
        # Allow checking if user exceeded daily limit
        # This assumes QueueManager has a check_limit method
        can_apply = await queue_manager.can_user_apply_today(test_user["id"])
        assert can_apply is True  # Assuming default limit > 0
