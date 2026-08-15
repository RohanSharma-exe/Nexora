"""Runtime contracts connecting perception, decisions, actions, and events."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EventType(StrEnum):
    """Types of events that can affect the simulated world."""

    MESSAGE_RECEIVED = "message_received"
    JOB_DISCOVERED = "job_discovered"
    JOB_COMPLETED = "job_completed"
    INFORMATION_DISCOVERED = "information_discovered"
    INFORMATION_SHARED = "information_shared"
    RELATIONSHIP_CHANGED = "relationship_changed"
    REPUTATION_CHANGED = "reputation_changed"


class ActionType(StrEnum):
    """High-level actions an NPC can request."""

    IDLE = "idle"
    COMPLETE_JOB = "complete_job"
    SEND_MESSAGE = "send_message"
    SHARE_INFORMATION = "share_information"
    WAIT = "wait"


@dataclass(frozen=True)
class Observation:
    """Information currently visible to an NPC."""

    subject_id: str
    tick: int
    events: tuple[str, ...] = ()
    memories: tuple[str, ...] = ()
    goals: tuple[str, ...] = ()
    contacts: tuple[str, ...] = ()
    available_actions: tuple[str, ...] = ()
    available_jobs: tuple[str, ...] = ()
    available_job_scores: tuple[tuple[str, float], ...] = ()


@dataclass(frozen=True)
class ActionIntent:
    """An action proposed by an NPC brain."""

    actor_id: str
    action_type: ActionType
    target_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""


@dataclass(frozen=True)
class ActionResult:
    """Result produced after validating and executing an action."""

    success: bool
    action_type: ActionType
    actor_id: str
    message: str
    effects: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorldEvent:
    """Immutable event emitted by the simulation runtime."""

    event_type: EventType
    tick: int
    actor_id: str
    target_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
