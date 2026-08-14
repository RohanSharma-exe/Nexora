from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class Memory:
    """A single event remembered by an NPC."""

    content: str
    importance: float
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class MemoryStore:
    """Simple in-memory episodic memory for V0."""

    def __init__(self) -> None:
        self._memories: list[Memory] = []

    def add(self, content: str, importance: float = 0.5) -> None:
        self._memories.append(
            Memory(
                content=content,
                importance=importance,
            )
        )

    def recent(self, limit: int = 5) -> list[Memory]:
        return self._memories[-limit:]

    def all(self) -> list[Memory]:
        return list(self._memories)
