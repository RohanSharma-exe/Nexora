from nexora.agent.rule_brain import RuleBasedBrain
from nexora.models.runtime import ActionType, GoalObservation, Observation


def make_observation(
    *,
    ambition: float,
    greed: float,
    risk_tolerance: float,
    patience: float,
) -> Observation:
    return Observation(
        subject_id="alice",
        tick=1,
        money=1000.0,
        energy=1.0,
        reputation=0.5,
        skills=("python", "fastapi"),
        personality=(
            ("ambition", ambition),
            ("curiosity", 0.5),
            ("greed", greed),
            ("patience", patience),
            ("risk_tolerance", risk_tolerance),
            ("sociability", 0.5),
        ),
        goals=("Earn ₹5000",),
        goal_details=(
            GoalObservation(
                description="Earn ₹5000",
                priority=1.0,
                progress=0.0,
                target_amount=5000.0,
            ),
        ),
        available_actions=("complete_job", "wait"),
        available_jobs=("safe-job", "risky-job"),
        available_job_scores=(
            ("safe-job", 2200.0),
            ("risky-job", 4200.0),
        ),
        available_job_risks=(
            ("safe-job", 0.05),
            ("risky-job", 0.90),
        ),
    )


def test_risk_tolerant_npc_prefers_higher_value_opportunity() -> None:
    brain = RuleBasedBrain()

    observation = make_observation(
        ambition=0.9,
        greed=0.8,
        risk_tolerance=0.95,
        patience=0.2,
    )

    intent = brain.decide(observation)

    assert intent.action_type == ActionType.COMPLETE_JOB
    assert intent.target_id == "risky-job"


def test_patient_risk_averse_npc_can_prefer_safer_opportunity() -> None:
    brain = RuleBasedBrain()

    observation = make_observation(
        ambition=0.3,
        greed=0.2,
        risk_tolerance=0.0,
        patience=0.95,
    )

    intent = brain.decide(observation)

    assert intent.action_type == ActionType.COMPLETE_JOB
    assert intent.target_id == "safe-job"
