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


def test_helpful_response_increases_sender_trust() -> None:
    social = SocialSystem(
        job_board=JobBoard(
            [
                Job(
                    id="job-1",
                    title="Python API Developer",
                    description="Build an API.",
                    payment=2500,
                    required_skills=["python"],
                )
            ]
        )
    )

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    bob = NPC(
        id="bob",
        name="Bob",
        occupation="Developer",
        skills=["python"],
    )

    social.register_npc(alice)
    social.register_npc(bob)

    social.send_message(
        sender_id="alice",
        recipient_id="bob",
        content="Do you know of any work?",
        tick=1,
        intent=MessageIntent.REQUEST,
    )

    agent = Agent(
        npc=bob,
        job_board=social.job_board or JobBoard(),
        social=social,
    )

    before = social.get_relationship(
        "alice",
        "bob",
    ).trust

    result = agent.process_message(
        current_tick=3,
    )

    assert result is not None
    assert result.success

    after = social.get_relationship(
        "alice",
        "bob",
    ).trust

    assert after > before


def test_helpful_response_increases_sender_trust_and_reputation() -> None:
    jobs = JobBoard(
        [
            Job(
                id="job-1",
                title="Python API Developer",
                description="Build an API.",
                payment=2500,
                required_skills=["python"],
            )
        ]
    )

    social = SocialSystem(
        job_board=jobs,
    )

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    bob = NPC(
        id="bob",
        name="Bob",
        occupation="Developer",
        skills=["python"],
    )

    social.register_npc(alice)
    social.register_npc(bob)

    social.send_message(
        sender_id="alice",
        recipient_id="bob",
        content="Do you know of any work?",
        tick=1,
        intent=MessageIntent.REQUEST,
    )

    agent = Agent(
        npc=bob,
        job_board=jobs,
        social=social,
    )

    before_trust = social.get_relationship(
        "alice",
        "bob",
    ).trust

    before_reputation = bob.reputation

    result = agent.process_message(
        current_tick=3,
    )

    assert result is not None
    assert result.success

    after_trust = social.get_relationship(
        "alice",
        "bob",
    ).trust

    after_reputation = bob.reputation

    assert after_trust > before_trust
    assert after_reputation > before_reputation


def test_neutral_response_does_not_change_reputation() -> None:
    social = SocialSystem(
        job_board=JobBoard(),
    )

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    bob = NPC(
        id="bob",
        name="Bob",
        occupation="Developer",
    )

    social.register_npc(alice)
    social.register_npc(bob)

    social.send_message(
        sender_id="alice",
        recipient_id="bob",
        content="Do you know of any work?",
        tick=1,
        intent=MessageIntent.REQUEST,
    )

    agent = Agent(
        npc=bob,
        job_board=social.job_board or JobBoard(),
        social=social,
    )

    before = bob.reputation

    result = agent.process_message(
        current_tick=3,
    )

    assert result is not None
    assert result.success
    assert bob.reputation == before


def test_helpful_response_increases_reputation() -> None:
    jobs = JobBoard(
        [
            Job(
                id="job-1",
                title="Python API Developer",
                description="Build an API.",
                payment=2500,
                required_skills=["python"],
            )
        ]
    )

    social = SocialSystem(
        job_board=jobs,
    )

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    bob = NPC(
        id="bob",
        name="Bob",
        occupation="Developer",
        skills=["python"],
    )

    social.register_npc(alice)
    social.register_npc(bob)

    social.send_message(
        sender_id="alice",
        recipient_id="bob",
        content="Do you know of any work?",
        tick=1,
        intent=MessageIntent.REQUEST,
    )

    agent = Agent(
        npc=bob,
        job_board=jobs,
        social=social,
    )

    before = bob.reputation

    result = agent.process_message(
        current_tick=3,
    )

    assert result is not None
    assert result.success
    assert bob.reputation > before
