from nexora.core.events import EventBus
from nexora.models.runtime import (
    ActionIntent,
    ActionResult,
    ActionType,
    EventType,
    Observation,
    WorldEvent,
)


def test_observation_is_immutable() -> None:
    observation = Observation(
        subject_id="alice",
        tick=10,
        events=("Bob sent a message.",),
        memories=("Bob helped Alice.",),
        goals=("Earn ₹5000",),
        contacts=("bob",),
        available_actions=("send_message", "wait"),
    )

    assert observation.subject_id == "alice"
    assert observation.tick == 10
    assert "bob" in observation.contacts


def test_action_intent_contains_actor_and_action() -> None:
    intent = ActionIntent(
        actor_id="alice",
        action_type=ActionType.SEND_MESSAGE,
        target_id="bob",
        payload={"content": "Hello Bob"},
        reasoning="Alice wants to reconnect with Bob.",
    )

    assert intent.actor_id == "alice"
    assert intent.action_type == ActionType.SEND_MESSAGE
    assert intent.target_id == "bob"
    assert intent.payload["content"] == "Hello Bob"


def test_action_result_records_effects() -> None:
    result = ActionResult(
        success=True,
        action_type=ActionType.SEND_MESSAGE,
        actor_id="alice",
        message="Message sent.",
        effects=("relationship_familiarity+0.05",),
    )

    assert result.success
    assert result.actor_id == "alice"
    assert result.effects == ("relationship_familiarity+0.05",)


def test_event_bus_delivers_events() -> None:
    bus = EventBus()
    received: list[WorldEvent] = []

    bus.subscribe(
        EventType.MESSAGE_RECEIVED,
        received.append,
    )

    event = WorldEvent(
        event_type=EventType.MESSAGE_RECEIVED,
        tick=5,
        actor_id="alice",
        target_id="bob",
        payload={"content": "Hello Bob"},
    )

    bus.publish(event)

    assert received == [event]


def test_event_bus_supports_multiple_handlers() -> None:
    bus = EventBus()

    first: list[WorldEvent] = []
    second: list[WorldEvent] = []

    bus.subscribe(EventType.JOB_DISCOVERED, first.append)
    bus.subscribe(EventType.JOB_DISCOVERED, second.append)

    event = WorldEvent(
        event_type=EventType.JOB_DISCOVERED,
        tick=1,
        actor_id="alice",
    )

    bus.publish(event)

    assert first == [event]
    assert second == [event]


def test_event_bus_does_not_call_handlers_for_other_event_types() -> None:
    bus = EventBus()
    received: list[WorldEvent] = []

    bus.subscribe(EventType.JOB_COMPLETED, received.append)

    event = WorldEvent(
        event_type=EventType.MESSAGE_RECEIVED,
        tick=1,
        actor_id="alice",
    )

    bus.publish(event)

    assert received == []
