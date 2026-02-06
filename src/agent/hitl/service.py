import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.hitl.schemas import (
    InterventionContext,
    InterventionResponse,
    InterventionStatus,
    InterventionType,
)
from src.agent.models.entities import AgentIntervention
from src.core.database.connection import get_db_context
from src.core.infrastructure.redis import redis_provider

logger = logging.getLogger(__name__)


class InterventionService:
    """
    Service for managing human-in-the-loop interventions.
    """

    async def request_intervention(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        intervention_type: InterventionType,
        context: InterventionContext,
        timeout_minutes: int = 30,
    ) -> AgentIntervention:
        """
        Create intervention request, notify user, wait for response.
        """
        async with get_db_context() as session:
            # Create DB record
            intervention = AgentIntervention(
                id=uuid.uuid4(),
                session_id=session_id,
                user_id=user_id,
                type=intervention_type,
                status=InterventionStatus.PENDING,
                context=context.model_dump(),
                expires_at=datetime.now(timezone.utc)
                + timedelta(minutes=timeout_minutes),
                created_at=datetime.now(timezone.utc),
            )
            session.add(intervention)
            await session.commit()
            await session.refresh(intervention)

            # Notify user via Redis pub/sub -> SSE
            await self._notify_user(user_id, intervention)

            return intervention

    async def _notify_user(self, user_id: uuid.UUID, intervention: AgentIntervention):
        """
        Push notification to frontend via Redis.
        """
        message = {
            "type": "intervention_needed",
            "intervention_id": str(intervention.id),
            "intervention_type": str(intervention.type),
            "job": intervention.context.get("job_title", "Unknown Job"),
            "company": intervention.context.get("company", "Unknown Company"),
            "urgency": "high",
        }
        channel = f"user:{user_id}:notifications"
        await redis_provider.publish(channel, json.dumps(message))

    async def wait_for_response(
        self, intervention_id: uuid.UUID, timeout_seconds: int = 1800
    ) -> InterventionResponse | None:
        """
        Poll DB for response. Used by the agent while paused.
        Returns None if timed out.
        """
        deadline = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)

        # Check frequency config
        poll_interval = 2  # seconds

        while datetime.now(timezone.utc) < deadline:
            async with get_db_context() as session:
                stmt = select(AgentIntervention).where(
                    AgentIntervention.id == intervention_id
                )
                result = await session.execute(stmt)
                intervention = result.scalar_one_or_none()

                if not intervention:
                    logger.error(
                        f"Intervention {intervention_id} not found during wait"
                    )
                    return None

                if intervention.status == InterventionStatus.RESPONDED:
                    if intervention.response:
                        return InterventionResponse(**intervention.response)
                    return None

                if intervention.status in [
                    InterventionStatus.EXPIRED,
                    InterventionStatus.SKIPPED,
                ]:
                    return None

            await asyncio.sleep(poll_interval)

            # Decrease polling frequency over time if needed, but 2s is fine for local

        # Mark as expired
        await self._mark_expired(intervention_id)
        return None

    async def _mark_expired(self, intervention_id: uuid.UUID):
        async with get_db_context() as session:
            stmt = (
                update(AgentIntervention)
                .where(AgentIntervention.id == intervention_id)
                .where(AgentIntervention.status == InterventionStatus.PENDING)
                .values(status=InterventionStatus.EXPIRED)
            )
            await session.execute(stmt)
            await session.commit()

    async def respond_to_intervention(
        self,
        intervention_id: uuid.UUID,
        user_id: uuid.UUID,
        response: InterventionResponse,
    ) -> bool:
        """Called by API when user responds."""
        async with get_db_context() as session:
            stmt = select(AgentIntervention).where(
                AgentIntervention.id == intervention_id
            )
            result = await session.execute(stmt)
            intervention = result.scalar_one_or_none()

            if not intervention:
                return False

            if intervention.user_id != user_id:
                raise PermissionError(
                    "User does not own this intervention"
                )  # In API layer catch this

            if intervention.status != InterventionStatus.PENDING:
                return False  # Already responded or expired

            intervention.response = response.model_dump()
            intervention.status = InterventionStatus.RESPONDED
            intervention.responded_at = datetime.now(timezone.utc)

            await session.commit()

            # Notify agent?
            # The agent is polling, so it will pick it up on next poll.
            # But we can also publish to an agent channel if we move to push-based agent later.
            return True

    async def get_pending_interventions(
        self, user_id: uuid.UUID
    ) -> list[AgentIntervention]:
        async with get_db_context() as session:
            stmt = (
                select(AgentIntervention)
                .where(AgentIntervention.user_id == user_id)
                .where(AgentIntervention.status == InterventionStatus.PENDING)
                .order_by(AgentIntervention.created_at.desc())
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_intervention(
        self, intervention_id: uuid.UUID, user_id: uuid.UUID
    ) -> AgentIntervention | None:
        async with get_db_context() as session:
            stmt = (
                select(AgentIntervention)
                .where(AgentIntervention.id == intervention_id)
                .where(AgentIntervention.user_id == user_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
