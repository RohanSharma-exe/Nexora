import pytest

from nexora.llm.brain import LLMBrain
from nexora.llm.provider import LLMProvider
from nexora.models.runtime import ActionIntent, ActionType, Observation


class FakeProvider(LLMProvider):
    """Deterministic provider used to test LLMBrain validation."""

    def __init__(self, intent: ActionIntent) -> None:
        self.intent = intent

    def decide(self, observation: Observation) -> ActionIntent:
        return self.intent


def make_observation() -> Observation:
    return Observation(
        subject_id="alice",
        tick=1,
        goals=("Earn ₹5000",),
        available_actions=("complete_job", "wait"),
        available_jobs=("job-1",),
    )


def test_llm_brain_delegates_to_provider() -> None:
    observation = make_observation()
    intent = ActionIntent(
        actor_id="alice",
        action_type=ActionType.COMPLETE_JOB,
        target_id="job-1",
    )

    brain = LLMBrain(FakeProvider(intent))

    result = brain.decide(observation)

    assert result == intent


def test_llm_brain_rejects_wrong_actor() -> None:
    observation = make_observation()
    intent = ActionIntent(
        actor_id="bob",
        action_type=ActionType.COMPLETE_JOB,
        target_id="job-1",
    )

    brain = LLMBrain(FakeProvider(intent))

    with pytest.raises(ValueError, match="actor"):
        brain.decide(observation)


def test_llm_brain_rejects_unavailable_action() -> None:
    observation = make_observation()
    intent = ActionIntent(
        actor_id="alice",
        action_type=ActionType.SEND_MESSAGE,
        target_id="bob",
    )

    brain = LLMBrain(FakeProvider(intent))

    with pytest.raises(ValueError, match="not currently available"):
        brain.decide(observation)


def test_llm_brain_rejects_unavailable_job() -> None:
    observation = make_observation()
    intent = ActionIntent(
        actor_id="alice",
        action_type=ActionType.COMPLETE_JOB,
        target_id="job-999",
    )

    brain = LLMBrain(FakeProvider(intent))

    with pytest.raises(ValueError, match="not available"):
        brain.decide(observation)
