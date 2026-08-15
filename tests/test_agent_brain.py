from nexora.agent.agent import Agent
from nexora.agent.rule_brain import RuleBasedBrain
from nexora.core.jobs import JobBoard
from nexora.memory.memory import MemoryStore
from nexora.models.job import Job
from nexora.models.npc import NPC, Goal
from nexora.models.runtime import ActionType
from nexora.social import SocialSystem


def create_agent() -> Agent:
    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Python Developer",
        skills=["python"],
        goals=[
            Goal(
                description="Earn ₹5000",
                priority=1.0,
                target_amount=5000,
            )
        ],
    )

    jobs = JobBoard(
        [
            Job(
                id="job-1",
                title="Python API Developer",
                description="Build a Python API.",
                payment=2500,
                required_skills=["python"],
            )
        ]
    )

    social = SocialSystem(
        job_board=jobs,
    )

    social.register_npc(npc)

    return Agent(
        npc=npc,
        job_board=jobs,
        social=social,
        memory=MemoryStore(),
        brain=RuleBasedBrain(),
    )


def test_agent_can_build_structured_observation() -> None:
    agent = create_agent()

    observation = agent.observe_structured(
        current_tick=5,
    )

    assert observation.subject_id == "alice"
    assert observation.tick == 5
    assert observation.goals == ("Earn ₹5000",)
    assert "complete_job" in observation.available_actions


def test_agent_can_make_brain_decision() -> None:
    agent = create_agent()

    intent = agent.decide_with_brain(
        current_tick=5,
    )

    assert intent.actor_id == "alice"
    assert intent.action_type == ActionType.COMPLETE_JOB
    assert intent.target_id == "job-1"


def test_agent_can_execute_brain_decision() -> None:
    agent = create_agent()

    result = agent.act_with_brain(
        current_tick=5,
    )

    assert result.npc_id == "alice"
    assert result.decision.action == ActionType.COMPLETE_JOB.value
    assert result.decision.target_id == "job-1"
    assert result.result.success
    assert agent.npc.money == 3500.0
