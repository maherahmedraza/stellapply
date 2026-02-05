import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any, Dict

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from src.agent.models.schemas import (
    AgentState,
    AgentStatus,
    AgentTaskCreate,
    AgentTaskResponse,
    AgentType,
    TaskPriority,
    TaskStatus,
)
from src.agent.tasks.celery_app import celery_app
from src.core.config import settings

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Coordinator for the autonomous agent system.

    This class runs as a singleton service within the API layer (or as a standalone service).
    It manages:
    1.  **Task Dispatch:** Receiving high-level user intents and converting them into
        task queues (Celery) for specific agents.
    2.  **Real-time Monitoring:** Maintaining WebSocket connections with the frontend
        to stream agent activities (logs, screenshots, decisions).
    3.  **Agent State Management:** Tracking which agents are busy/idle (via Redis).
    4.  **Inter-Process Communication:** Using Redis Pub/Sub to receive updates from
        worker processes (where the actual browser agents run) and broadcasting them
        to connected WebSockets.

    Attributes:
        redis (Redis): Async Redis client for state and pub/sub.
        active_websockets (Dict[uuid.UUID, list[WebSocket]]): Map of user_id to active WebSocket connections.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentOrchestrator, cls).__new__(cls)
            cls._instance.active_websockets = {}
            cls._instance.redis = None
        return cls._instance

    async def initialize(self):
        """
        Initialize Redis connection and start the background listener for Pub/Sub.
        """
        if not self.redis:
            self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            # Start background listener task
            asyncio.create_task(self._listen_to_agent_events())
            logger.info("Agent Orchestrator initialized.")

    async def shutdown(self):
        """
        Close Redis connection.
        """
        if self.redis:
            await self.redis.close()
            logger.info("Agent Orchestrator shutdown.")

    async def connect_websocket(self, user_id: uuid.UUID, websocket: WebSocket):
        """
        Register a new WebSocket connection for a user.
        """
        await websocket.accept()
        if user_id not in self.active_websockets:
            self.active_websockets[user_id] = []
        self.active_websockets[user_id].append(websocket)
        logger.info(f"User {user_id} connected to Agent Stream.")

        try:
            # Send initial state
            await websocket.send_json(
                {
                    "type": "connection_established",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "message": "Connected to Stellapply Agent Network",
                }
            )

            # Keep connection alive
            while True:
                # We mainly send data OUT, but we can listen for "stop" commands here
                data = await websocket.receive_text()
                # Handle client-side commands if necessary (e.g., "pause_agent")
                logger.debug(f"Received from {user_id}: {data}")

        except WebSocketDisconnect:
            logger.info(f"User {user_id} disconnected.")
            self.active_websockets[user_id].remove(websocket)
            if not self.active_websockets[user_id]:
                del self.active_websockets[user_id]

    async def dispatch_task(self, task_create: AgentTaskCreate) -> uuid.UUID:
        """
        Dispatch a new task to the appropriate agent queue.

        Args:
            task_create (AgentTaskCreate): The task definition.

        Returns:
            uuid.UUID: The assigned Task ID.
        """
        task_id = uuid.uuid4()

        # 1. Create DB record (Pseudo-code, actual implementation would use Repository)
        # await self.task_repository.create(task_create, task_id)

        # 2. Determine Celery Queue based on AgentType
        queue_map = {
            AgentType.SCOUT: "discovery",
            AgentType.APPLICANT: "application",
            AgentType.REGISTRAR: "application",  # Registrar shares queue or has own
        }
        queue = queue_map.get(task_create.type, "default")

        # 3. Construct payload for Celery
        celery_payload = {
            "task_id": str(task_id),
            "user_id": str(task_create.user_id),
            "payload": task_create.payload,
        }

        # 4. Send to Celery
        # We assume tasks are named 'src.agent.tasks.<type>.execute'
        task_name = f"src.agent.tasks.{task_create.type}.execute"

        celery_app.send_task(
            task_name,
            kwargs=celery_payload,
            queue=queue,
            priority=self._priority_to_int(task_create.priority),
        )

        logger.info(f"Dispatched task {task_id} ({task_create.type}) to queue {queue}")

        # 5. Notify user via WebSocket
        await self._broadcast_event(
            task_create.user_id,
            {
                "type": "task_dispatched",
                "task_id": str(task_id),
                "agent_type": task_create.type,
                "status": TaskStatus.PENDING,
            },
        )

        return task_id

    async def _broadcast_event(self, user_id: uuid.UUID, event: Dict[str, Any]):
        """
        Internal: Send an event to all active WebSockets for a specific user.
        """
        if user_id in self.active_websockets:
            sockets = self.active_websockets[user_id]
            to_remove = []
            for ws in sockets:
                try:
                    await ws.send_json(event)
                except Exception:
                    to_remove.append(ws)

            # Cleanup dead sockets
            for ws in to_remove:
                sockets.remove(ws)

    async def _listen_to_agent_events(self):
        """
        Background Task: Subscribe to Redis Pub/Sub channels to receive updates from
        worker agents (Browser/Celery runners) and forward them to WebSockets.

        Channel convention: "agent_events:<user_id>"
        """
        pubsub = self.redis.pubsub()
        # We subscribe to a glob pattern to catch all users or just listen to a global channel
        # For scalability in a single instance, we can subscribe to 'agent_events:*'
        # but pattern matching in Redis is expensive if high volume.
        # Better approach: All workers publish to "global_agent_events", orchestrator filters.

        await pubsub.subscribe("global_agent_events")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    user_id_str = data.get("user_id")
                    if user_id_str:
                        user_id = uuid.UUID(user_id_str)
                        await self._broadcast_event(user_id, data)
                except Exception as e:
                    logger.error(f"Error processing pub/sub message: {e}")

    def _priority_to_int(self, priority: TaskPriority) -> int:
        mapping = {
            TaskPriority.LOW: 0,
            TaskPriority.MEDIUM: 5,
            TaskPriority.HIGH: 9,
            TaskPriority.CRITICAL: 10,
        }
        return mapping.get(priority, 5)


# Singleton accessor
orchestrator = AgentOrchestrator()
