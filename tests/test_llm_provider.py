from nexora.llm.brain import LLMBrain
from nexora.llm.mock_provider import MockLLMProvider
from nexora.llm.schema import LLMAction
from nexora.models.runtime import ActionType, Observation


def make_observation() -> Observation:
    return Observation(
        subject_id="alice",
        tick=1,
        goals=("Earn ₹5000",),
        available_actions=("complete_job", "wait"),
        available_jobs=("job-1",),
    )


def test_mock_provider_returns_structured_action() -> None:
    provider = MockLLMProvider(
        LLMAction(
            action=ActionType.COMPLETE_JOB,
            target_id="job-1",
            reasoning="The job advances the active goal.",
        )
    )

    brain = LLMBrain(provider)
    intent = brain.decide(make_observation())

    assert intent.actor_id == "alice"
    assert intent.action_type == ActionType.COMPLETE_JOB
    assert intent.target_id == "job-1"
    assert intent.reasoning == "The job advances the active goal."


def test_mock_provider_can_generate_message_action() -> None:
    observation = Observation(
        subject_id="alice",
        tick=1,
        contacts=("bob",),
        available_actions=("send_message", "wait"),
    )

    provider = MockLLMProvider(
        LLMAction(
            action=ActionType.SEND_MESSAGE,
            target_id="bob",
            content="Hello Bob.",
            reasoning="Respond to Bob.",
        )
    )

    intent = LLMBrain(provider).decide(observation)

    assert intent.action_type == ActionType.SEND_MESSAGE
    assert intent.target_id == "bob"
    assert intent.payload == {"content": "Hello Bob."}
