import asyncio
import logging
import uuid
from typing import Any, Dict

from asgiref.sync import async_to_sync

from src.agent.agents.applicant import ApplicantAgent
from src.agent.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def execute(self, task_id: str, user_id: str, payload: Dict[str, Any]):
    """
    Celery task wrapper for the Applicant Agent.
    """
    task_uuid = uuid.UUID(task_id)
    user_uuid = uuid.UUID(user_id)

    logger.info(f"Starting Applicant Agent task {task_id}")

    async def _run_agent():
        agent = ApplicantAgent(user_uuid, task_uuid)
        return await agent.run(payload)

    try:
        # Run the async agent in the sync Celery worker
        result = async_to_sync(_run_agent)()
        logger.info(f"Applicant Agent task {task_id} completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Applicant Agent task {task_id} failed: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)
