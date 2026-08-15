from nexora.agent.brain import Brain
from nexora.agent.rule_brain import RuleBasedBrain
from nexora.models.runtime import (
    ActionType,
    Observation,
)


def test_rule_based_brain_implements_brain_interface() -> None:
    brain = RuleBasedBrain()

    assert isinstance(brain, Brain)


def test_brain_responds_to_incoming_event() -> None:
    brain = RuleBasedBrain()

    observation = Observation(
        subject_id="bob",
        tick=1,
        events=("alice sent a message",),
        available_actions=("send_message", "wait"),
    )

    intent = brain.decide(observation)

    assert intent.actor_id == "bob"
    assert intent.action_type == ActionType.SEND_MESSAGE


def test_brain_prioritizes_goal_progress_when_no_event_exists() -> None:
    brain = RuleBasedBrain()

    observation = Observation(
        subject_id="alice",
        tick=1,
        goals=("Earn ₹5000",),
        available_actions=("complete_job", "wait"),
    )

    intent = brain.decide(observation)

    assert intent.action_type == ActionType.COMPLETE_JOB


def test_brain_selects_highest_value_job() -> None:
    brain = RuleBasedBrain()

    observation = Observation(
        subject_id="alice",
        tick=1,
        goals=("Earn ₹5000",),
        available_actions=("complete_job", "wait"),
        available_jobs=("cheap-job", "valuable-job"),
        available_job_scores=(
            ("cheap-job", 1500.0),
            ("valuable-job", 4200.0),
        ),
    )

    intent = brain.decide(observation)

    assert intent.action_type == ActionType.COMPLETE_JOB
    assert intent.target_id == "valuable-job"


def test_brain_waits_when_no_goal_or_event_exists() -> None:
    brain = RuleBasedBrain()

    observation = Observation(
        subject_id="alice",
        tick=1,
        available_actions=("wait",),
    )

    intent = brain.decide(observation)

    assert intent.action_type == ActionType.WAIT


def test_brain_idles_when_nothing_is_available() -> None:
    brain = RuleBasedBrain()

    observation = Observation(
        subject_id="alice",
        tick=1,
    )

    intent = brain.decide(observation)

    assert intent.action_type == ActionType.IDLE
