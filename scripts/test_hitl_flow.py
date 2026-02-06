import asyncio
import uuid
import logging
from unittest.mock import MagicMock, AsyncMock

import src.core.database.all_models  # noqa
from src.agent.hitl.service import InterventionService
from src.agent.hitl.schemas import (
    InterventionType,
    InterventionContext,
    InterventionResponse,
)
from src.agent.models.entities import AgentIntervention
from src.core.infrastructure.redis import redis_provider
from src.agent.agents.base import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_hitl_flow():
    logger.info("Starting HITL Flow Verification...")

    # Mock Redis to avoid needing a real Redis instance for this snippet if possible,
    # but service uses real redis_provider.
    # Let's assume redis is running as per environment.

    # 0. Setup DB Prerequisites (User, AgentSession)
    from src.core.database.connection import get_db_context
    from src.modules.identity.domain.models import User
    from src.agent.models.entities import AgentSession

    async with get_db_context() as session:
        # Create User
        user = User(
            email=f"test_hitl_{uuid.uuid4()}@example.com",
            password_hash="pw",
            email_hash=f"hash_{uuid.uuid4()}",
        )
        session.add(user)
        await session.flush()
        user_id = user.id

        # Create AgentSession
        agent_session = AgentSession(
            user_id=user_id, config={"test": True}, state={}, status="running"
        )
        session.add(agent_session)
        await session.flush()
        session_id = agent_session.id
        await session.commit()

    logger.info(f"Created setup data: User={user_id}, Session={session_id}")

    service = InterventionService()

    # 1. Create Intervention
    logger.info("1. Creating Intervention...")
    context = InterventionContext(
        url="https://example.com/apply",
        question="What is your favorite color?",
        job_title="Test Job",
        company="Test Corp",
    )

    intervention = await service.request_intervention(
        session_id=session_id,
        user_id=user_id,
        intervention_type=InterventionType.UNKNOWN_QUESTION,
        context=context,
    )

    assert intervention.id is not None
    assert intervention.status == "pending"
    logger.info(f"Intervention created: {intervention.id}")

    # 2. Simulate User Response (via API logic)
    logger.info("2. Simulating User Response...")

    # Verify it exists in pending list
    pending = await service.get_pending_interventions(user_id)
    assert len(pending) >= 1
    assert str(intervention.id) in [str(i.id) for i in pending]

    response_payload = InterventionResponse(action="provide_answer", value="Blue")

    success = await service.respond_to_intervention(
        intervention.id, user_id, response_payload
    )
    assert success is True
    logger.info("Response submitted successfully.")

    # 3. Verify status update
    updated_intervention = await service.get_intervention(intervention.id, user_id)
    assert updated_intervention.status == "responded"
    assert updated_intervention.response["value"] == "Blue"
    logger.info("Intervention status verified as RESPONDED.")

    logger.info("HITL Flow Verification PASSED ✅")


if __name__ == "__main__":
    asyncio.run(test_hitl_flow())
