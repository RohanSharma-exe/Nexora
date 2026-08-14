from nexora.agent.decision import DecisionEngine
from nexora.core.jobs import JobBoard
from nexora.models.job import Job, JobDifficulty
from nexora.models.npc import NPC, Personality


def create_jobs() -> JobBoard:
    return JobBoard(
        [
            Job(
                id="easy",
                title="Easy Task",
                description="Simple Python task.",
                payment=1500,
                required_skills=["python"],
                difficulty=JobDifficulty.EASY,
            ),
            Job(
                id="medium",
                title="Medium Task",
                description="Medium Python task.",
                payment=2500,
                required_skills=["python"],
                difficulty=JobDifficulty.MEDIUM,
            ),
            Job(
                id="hard",
                title="Hard Task",
                description="Difficult FastAPI task.",
                payment=3500,
                required_skills=["python"],
                difficulty=JobDifficulty.HARD,
            ),
        ]
    )


def create_npc(personality: Personality) -> NPC:
    from nexora.models.npc import Goal

    return NPC(
        id="npc",
        name="NPC",
        occupation="Developer",
        skills=["python"],
        personality=personality,
        goals=[
            Goal(
                description="Earn ₹5000",
                priority=1.0,
                target_amount=5000,
            )
        ],
    )


def test_high_risk_npc_prefers_hard_high_payment_job() -> None:
    npc = create_npc(
        Personality(
            ambition=0.9,
            curiosity=0.8,
            risk_tolerance=0.9,
            sociability=0.5,
            greed=0.8,
            patience=0.2,
        )
    )

    decision = DecisionEngine().decide(
        npc,
        create_jobs(),
    )

    assert decision.target_id == "hard"


def test_patient_risk_averse_npc_can_wait() -> None:
    npc = create_npc(
        Personality(
            ambition=0.2,
            curiosity=0.5,
            risk_tolerance=0.1,
            sociability=0.5,
            greed=0.1,
            patience=0.9,
        )
    )

    decision = DecisionEngine().decide(
        npc,
        create_jobs(),
    )

    assert decision.action == "wait"
