import asyncio
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


class Event(BaseModel):
    pass


class InternalEventBus:
    def __init__(self) -> None:
        self._subscribers: dict[type[Event], list[Callable[[Event], Any]]] = {}

    def subscribe(
        self, event_type: type[Event], handler: Callable[[Event], Any]
    ) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event: Event) -> None:
        event_type = type(event)
        if event_type in self._subscribers:
            tasks = [handler(event) for handler in self._subscribers[event_type]]
            await asyncio.gather(*tasks)


event_bus = InternalEventBus()
