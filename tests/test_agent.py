from nexora.agent.agent import Agent
from nexora.core.jobs import JobBoard
from nexora.models.conversation import MessageIntent
from nexora.models.job import Job
from nexora.models.npc import NPC, Goal, Personality
from nexora.social import SocialSystem


def test_active_goal_is_not_starved_by_messages() -> None:
    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        skills=["python"],
        personality=Personality(
            sociability=1.0,
        ),
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
                title="Python Job",
                description="Build an API.",
                payment=2000,
                required_skills=["python"],
            )
        ]
    )

    social = SocialSystem(
        job_board=jobs,
    )
    social.register_npc("alice")
    social.register_npc("bob")

    social.send_message(
        sender_id="bob",
        recipient_id="alice",
        content="Hey Alice!",
        tick=1,
        intent=MessageIntent.GREETING,
    )

    agent = Agent(
        npc=npc,
        job_board=jobs,
        social=social,
    )

    result = agent.tick()

    assert result.decision.action == "complete_job"
    assert npc.money == 3000
