import asyncio
from uuid import UUID
from celery import shared_task
from sqlalchemy import select
from src.core.database.connection import get_db_context
from src.agent.orchestrator import AgentOrchestrator
from src.agent.browser.pool import BrowserPool
from src.agent.models.entities import AgentSession
from src.agent.models.pipeline import PipelineConfig
from src.modules.profile.schemas import UserProfileResponse


@shared_task(bind=True)
def run_agent_pipeline(self, session_id: str, user_id: str):
    """
    Celery task to run the agent pipeline.
    """

    async def _run():
        async with get_db_context() as db:
            agent_session = None
            try:
                session_uuid = UUID(session_id)
                user_uuid = UUID(user_id)

                # Load Session
                result = await db.execute(
                    select(AgentSession).where(AgentSession.id == session_uuid)
                )
                agent_session = result.scalars().first()
                if not agent_session:
                    return

                agent_session.status = "running"
                await db.commit()

                # Load User Profile
                from src.modules.profile.service_helper import get_user_profile_schema

                profile = await get_user_profile_schema(db, user_uuid)

                if not profile:
                    agent_session.status = "failed"
                    agent_session.result = {"error": "User profile not found"}
                    await db.commit()
                    return

                config = PipelineConfig(**agent_session.config)

                browser_pool = BrowserPool()
                orchestrator = AgentOrchestrator(user_uuid, session_uuid, browser_pool)

                result = await orchestrator.run_pipeline(config, profile)

                agent_session.result = result.model_dump()
                agent_session.status = "completed"
                await db.commit()

            except Exception as e:
                # Need to rollback or re-fetch session if we want to save error
                # In async context manager, rollback happens on raise, but we want to save fail state
                # So we catch, save, then maybe re-raise
                if agent_session:
                    # Should probably fetch fresh or ensure session is attached
                    agent_session.status = "failed"
                    # Log error details if needed
                    await db.commit()
                raise e

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_run())
    finally:
        loop.close()
