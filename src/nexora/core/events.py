"""Event bus for decoupling simulation subsystems."""

from collections.abc import Callable

from nexora.models.runtime import WorldEvent

EventHandler = Callable[[WorldEvent], None]


class EventBus:
    """Simple synchronous event bus for the simulation runtime."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """Register a handler for an event type."""

        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event: WorldEvent) -> None:
        """Publish an event to all subscribed handlers."""

        handlers = self._handlers.get(event.event_type, [])

        for handler in handlers:
            handler(event)

    def clear(self) -> None:
        """Remove all registered handlers."""

        self._handlers.clear()
