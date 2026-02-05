import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, WebSocket, status

from src.agent.models.schemas import AgentTaskCreate, AgentTaskResponse
from src.agent.orchestrator import orchestrator
from src.api.middleware.auth import get_current_user
from src.modules.identity.infrastructure.keycloak import KeycloakProvider

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/tasks", response_model=AgentTaskResponse, status_code=status.HTTP_201_CREATED
)
async def create_agent_task(
    task: AgentTaskCreate,
    current_user: dict = Depends(get_current_user),  # noqa: B008
) -> dict:
    """
    Trigger a new autonomous agent task.
    """
    user_id = uuid.UUID(current_user["sub"])

    # Ensure user_id matches or is authorized
    if task.user_id != user_id:
        # Simple authorization check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create tasks for other users",
        )

    task_id = await orchestrator.dispatch_task(task)

    # In a real implementation, we would return the full persisted task object.
    # For now, we return the ID and echo back the input with status.
    return {
        "id": task_id,
        "type": task.type,
        "status": "pending",
        "priority": task.priority,
        "payload": task.payload,
        "user_id": user_id,
        "created_at": "2024-01-01T00:00:00Z",  # Placeholder, would come from DB
        "updated_at": "2024-01-01T00:00:00Z",
    }


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str | None = None,
):
    """
    Real-time stream for agent activities.
    Authenticate via query param `?token=...`.
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        # Verify token using Keycloak
        keycloak = KeycloakProvider()
        # This will raise exception if invalid
        user_payload = keycloak.decode_token(token)
        user_id = uuid.UUID(user_payload["sub"])

        await orchestrator.connect_websocket(user_id, websocket)

    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
