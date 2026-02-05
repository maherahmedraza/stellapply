import asyncio
import logging
import time
from collections.abc import Callable, Awaitable
from typing import Any, TypeVar, Optional, Dict, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="Event")


class Event(BaseModel):
    """Base class for all internal events."""

    event_id: UUID = Field(default_factory=uuid4)
    timestamp: float = Field(default_factory=time.time)


class EventPublishResult(BaseModel):
    """Result of an event publication."""

    event_id: UUID
    handlers_called: int
    handlers_succeeded: int
    handlers_failed: int
    errors: List[str] = []


class InternalEventBus:
    """
    Robust in-process event bus with handler isolation and async support.
    Ensures that failures in one handler do not affect others.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[type, List[Callable[[Any], Awaitable[Any]]]] = {}
        self._dead_letter_queue: List[Dict[str, Any]] = []

    def subscribe(
        self, event_type: type[T], handler: Callable[[T], Awaitable[Any]]
    ) -> None:
        """Register a handler for a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed {handler.__name__} to {event_type.__name__}")

    async def publish(
        self, event: Event, wait_for_handlers: bool = True
    ) -> EventPublishResult:
        """
        Publish an event to all registered subscribers.

        Args:
            event: The event instance to publish
            wait_for_handlers: If True, waits for all handlers to complete.
                              If False, handlers run in the background.
        """
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])

        if not handlers:
            return EventPublishResult(
                event_id=event.event_id,
                handlers_called=0,
                handlers_succeeded=0,
                handlers_failed=0,
            )

        logger.info(
            f"Publishing {event_type.__name__} ({event.event_id}) to {len(handlers)} handlers"
        )

        if wait_for_handlers:
            return await self._execute_handlers(event, handlers)
        else:
            # Fire and forget
            asyncio.create_task(self._execute_handlers(event, handlers))
            return EventPublishResult(
                event_id=event.event_id,
                handlers_called=len(handlers),
                handlers_succeeded=0,
                handlers_failed=0,
            )

    async def _execute_handlers(
        self, event: Event, handlers: List[Callable[[Any], Awaitable[Any]]]
    ) -> EventPublishResult:
        """Execute handlers with individual error isolation and timeouts."""
        succeeded = 0
        failed = 0
        errors = []

        for handler in handlers:
            try:
                # Wrap in timeout to prevent hanging handlers
                await asyncio.wait_for(handler(event), timeout=10.0)
                succeeded += 1
            except asyncio.TimeoutError:
                failed += 1
                error_msg = f"Handler {handler.__name__} timed out after 10s"
                logger.error(error_msg)
                errors.append(error_msg)
                self._handle_failure(event, handler, "Timeout")
            except Exception as e:
                failed += 1
                error_msg = f"Handler {handler.__name__} failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
                self._handle_failure(event, handler, str(e))

        return EventPublishResult(
            event_id=event.event_id,
            handlers_called=len(handlers),
            handlers_succeeded=succeeded,
            handlers_failed=failed,
            errors=errors,
        )

    def _handle_failure(self, event: Event, handler: Callable, error: str) -> None:
        """Log failure and add to internal dead-letter queue for debugging."""
        self._dead_letter_queue.append(
            {
                "event": event.model_dump(),
                "handler": handler.__name__,
                "error": error,
                "timestamp": time.time(),
            }
        )
        # Keep queue size manageable
        if len(self._dead_letter_queue) > 100:
            self._dead_letter_queue.pop(0)


# Global instances
event_bus = InternalEventBus()
