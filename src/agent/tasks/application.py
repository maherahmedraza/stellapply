import asyncio
import logging
import uuid
from typing import Any, Dict

from asgiref.sync import async_to_sync

from src.agent.agents.applicant import ApplicantAgent
from src.agent.tasks.celery_app import celery_app
from src.core.database.connection import get_db_context
from src.modules.profile.service import ProfileService

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
        # Fetch fresh profile data
        async with get_db_context() as session:
            service = ProfileService(session)
            profile = await service.get_by_user_id(user_uuid)

            # Simple serialization - in real world use Pydantic helpers
            # For now, we manually expand the encrypted/json fields
            import json

            profile_data = {
                "personal_info": json.loads(profile.personal_info)
                if profile.personal_info
                else {},
                "search_preferences": profile.search_preferences,
                "agent_rules": profile.agent_rules,
                "application_answers": json.loads(profile.application_answers)
                if profile.application_answers
                else {},
                "resume_strategy": profile.resume_strategy,
            }

            # Merge with existing payload, prioritizing payload overrides if any
            full_payload = {**payload, "profile_data": profile_data}

        agent = ApplicantAgent(user_uuid, task_uuid)
        return await agent.run(full_payload)

    try:
        # Run the async agent in the sync Celery worker
        result = async_to_sync(_run_agent)()
        logger.info(f"Applicant Agent task {task_id} completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Applicant Agent task {task_id} failed: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)
