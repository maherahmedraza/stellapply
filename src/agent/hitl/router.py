import asyncio
import collections.abc
import json
import logging
import uuid
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from src.agent.hitl.schemas import (
    AgentIntervention,
    InterventionResponse,
    CreateInterventionRequest,  # Internal use
)
from src.agent.hitl.service import InterventionService
from src.core.infrastructure.redis import redis_provider
from src.api.middleware.auth import get_current_user
from src.modules.identity.domain.models import User

router = APIRouter(prefix="/interventions", tags=["Agent Interventions"])
logger = logging.getLogger(__name__)

service = InterventionService()


@router.get("/", response_model=list[AgentIntervention])
async def list_pending_interventions(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    List all pending interventions for the current user.
    """
    return await service.get_pending_interventions(current_user.id)


@router.get("/{intervention_id}", response_model=AgentIntervention)
async def get_intervention(
    intervention_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get detailed context for a specific intervention.
    """
    intervention = await service.get_intervention(intervention_id, current_user.id)
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found"
        )
    return intervention


@router.post("/{intervention_id}/respond")
async def respond_to_intervention(
    intervention_id: uuid.UUID,
    response: InterventionResponse,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Submit a human response to an agent request.
    """
    try:
        success = await service.respond_to_intervention(
            intervention_id, current_user.id, response
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Intervention is not pending or expired",
            )
        return {"status": "success"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/stream")
async def stream_interventions(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    SSE stream for real-time intervention notifications.
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        channel = f"user:{current_user.id}:notifications"
        pubsub = redis_provider._client.pubsub()
        await pubsub.subscribe(channel)

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = message["data"]
                    yield f"data: {data}\n\n"
                await asyncio.sleep(
                    1
                )  # Refresh rate equivalent, mostly relies on pubsub push
        except asyncio.CancelledError:
            await pubsub.unsubscribe(channel)
            logger.info(f"SSE stream closed for user {current_user.id}")

    return StreamingResponse(event_generator(), media_type="text/event-stream")
