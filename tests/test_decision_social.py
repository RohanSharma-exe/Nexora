from nexora.agent.decision import DecisionEngine
from nexora.core.jobs import JobBoard
from nexora.models.job import Job
from nexora.models.npc import NPC, Goal, Personality
from nexora.social import SocialSystem


def test_active_goal_has_priority_over_social() -> None:
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

    social = SocialSystem()
    social.register_npc("alice")
    social.register_npc("bob")

    decision = DecisionEngine().decide(
        npc,
        jobs,
        social,
    )

    assert decision.action == "complete_job"
    assert decision.target_id == "job-1"


def test_social_npc_initiates_when_no_goal() -> None:
    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        personality=Personality(
            sociability=1.0,
        ),
    )

    social = SocialSystem()
    social.register_npc("alice")
    social.register_npc("bob")

    decision = DecisionEngine().decide(
        npc,
        JobBoard(),
        social,
    )

    assert decision.action == "send_message"
    assert decision.target_id == "bob"


def test_goal_npc_asks_contact_when_no_jobs() -> None:
    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        skills=["python"],
        personality=Personality(
            sociability=0.8,
        ),
        goals=[
            Goal(
                description="Earn ₹5000",
                priority=1.0,
                target_amount=5000,
            )
        ],
    )

    social = SocialSystem()
    social.register_npc("alice")
    social.register_npc("bob")

    decision = DecisionEngine().decide(
        npc,
        JobBoard(),
        social,
    )

    assert decision.action == "send_message"
    assert decision.target_id == "bob"


def test_goal_npc_prefers_trusted_contact_when_no_jobs() -> None:
    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        skills=["python"],
        personality=Personality(
            sociability=0.8,
        ),
        goals=[
            Goal(
                description="Earn ₹5000",
                priority=1.0,
                target_amount=5000,
            )
        ],
    )

    social = SocialSystem()

    social.register_npc("alice")
    social.register_npc("bob")
    social.register_npc("sarah")

    social.send_message(
        sender_id="alice",
        recipient_id="bob",
        content="Hello",
        tick=1,
    )

    social.send_message(
        sender_id="alice",
        recipient_id="sarah",
        content="Hello",
        tick=1,
    )

    social.get_relationship(
        "alice",
        "sarah",
    ).trust = 0.95

    social.get_relationship(
        "alice",
        "bob",
    ).trust = 0.2

    decision = DecisionEngine().decide(
        npc,
        JobBoard(),
        social,
        current_tick=3,
    )

    assert decision.action == "send_message"
    assert decision.target_id == "sarah"
