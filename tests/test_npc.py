from nexora.agent.agent import Agent
from nexora.core.jobs import JobBoard
from nexora.models.job import Job
from nexora.models.npc import NPC, Goal
from nexora.social import SocialSystem


def create_npc() -> NPC:
    return NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        skills=["python"],
        money=1000,
        goals=[
            Goal(
                description="Earn ₹5000",
                priority=0.9,
                target_amount=5000,
            )
        ],
    )


def create_agent(npc: NPC) -> Agent:
    return Agent(
        npc=npc,
        job_board=JobBoard(),
        social=SocialSystem(),
    )


def test_npc_can_select_job() -> None:
    npc = create_npc()

    job_board = JobBoard(
        [
            Job(
                id="job-1",
                title="Python Job",
                description="Write Python code.",
                payment=2000,
                required_skills=["python"],
            )
        ]
    )

    agent = Agent(
        npc=npc,
        job_board=job_board,
        social=SocialSystem(),
    )

    decision = agent.decide()

    assert decision.action == "complete_job"
    assert decision.target_id == "job-1"


def test_agent_can_complete_job() -> None:
    npc = create_npc()

    job_board = JobBoard(
        [
            Job(
                id="job-1",
                title="Python Job",
                description="Write Python code.",
                payment=2000,
                required_skills=["python"],
            )
        ]
    )

    agent = Agent(
        npc=npc,
        job_board=job_board,
        social=SocialSystem(),
    )

    result = agent.tick()

    assert result.result.success is True
    assert npc.money == 3000
    assert npc.goals[0].progress == 2000
    assert npc.goals[0].completed is False


def test_agent_completes_earn_goal() -> None:
    npc = create_npc()

    job_board = JobBoard(
        [
            Job(
                id="job-1",
                title="Python Job",
                description="Write Python code.",
                payment=5000,
                required_skills=["python"],
            )
        ]
    )

    agent = Agent(
        npc=npc,
        job_board=job_board,
        social=SocialSystem(),
    )

    agent.tick()

    assert npc.money == 6000
    assert npc.goals[0].progress == 5000
    assert npc.goals[0].completed is True
