from nexora.agent.observation import ObservationBuilder
from nexora.core.jobs import JobBoard
from nexora.memory.memory import MemoryStore
from nexora.models.conversation import MessageIntent
from nexora.models.job import Job, JobDifficulty
from nexora.models.npc import NPC, Goal
from nexora.social import SocialSystem


def create_npc() -> NPC:
    return NPC(
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


def create_job_board() -> JobBoard:
    return JobBoard(
        [
            Job(
                id="job-1",
                title="Python API Developer",
                description="Build a Python API.",
                payment=2500,
                required_skills=["python"],
            ),
            Job(
                id="job-2",
                title="Design Landing Page",
                description="Design a landing page.",
                payment=2000,
                required_skills=["design"],
            ),
        ]
    )


def create_social() -> SocialSystem:
    social = SocialSystem(
        job_board=create_job_board(),
    )

    social.register_npc(create_npc())

    social.register_npc(
        NPC(
            id="bob",
            name="Bob",
            occupation="Backend Developer",
        )
    )

    return social


def test_observation_contains_active_goals() -> None:
    npc = create_npc()
    social = create_social()
    memory = MemoryStore()

    builder = ObservationBuilder(
        job_board=create_job_board(),
        social=social,
        memory=memory,
    )

    observation = builder.build(
        npc=npc,
        tick=10,
    )

    assert observation.subject_id == "alice"
    assert observation.tick == 10
    assert observation.goals == ("Earn ₹5000",)


def test_observation_contains_suitable_job_action() -> None:
    npc = create_npc()
    social = create_social()
    memory = MemoryStore()

    builder = ObservationBuilder(
        job_board=create_job_board(),
        social=social,
        memory=memory,
    )

    observation = builder.build(
        npc=npc,
        tick=1,
    )

    assert "complete_job" in observation.available_actions
    assert observation.available_jobs == ("job-1",)


def test_observation_excludes_completed_goals() -> None:
    npc = create_npc()
    npc.goals[0].completed = True

    social = create_social()
    memory = MemoryStore()

    builder = ObservationBuilder(
        job_board=create_job_board(),
        social=social,
        memory=memory,
    )

    observation = builder.build(
        npc=npc,
        tick=1,
    )

    assert observation.goals == ()
    assert "complete_job" not in observation.available_actions


def test_observation_contains_unread_messages() -> None:
    npc = create_npc()
    social = create_social()
    memory = MemoryStore()

    social.send_message(
        sender_id="bob",
        recipient_id="alice",
        content="Do you know of any Python work?",
        tick=1,
        intent=MessageIntent.REQUEST,
    )

    builder = ObservationBuilder(
        job_board=create_job_board(),
        social=social,
        memory=memory,
    )

    observation = builder.build(
        npc=npc,
        tick=2,
    )

    assert observation.events == ("bob: Do you know of any Python work?",)


def test_observation_contains_memories() -> None:
    npc = create_npc()
    social = create_social()
    memory = MemoryStore()

    memory.add(
        "Alice completed a FastAPI project.",
        importance=0.8,
    )

    memory.add(
        "Bob helped Alice find work.",
        importance=0.9,
    )

    builder = ObservationBuilder(
        job_board=create_job_board(),
        social=social,
        memory=memory,
    )

    observation = builder.build(
        npc=npc,
        tick=5,
    )

    assert observation.memories == (
        "Alice completed a FastAPI project.",
        "Bob helped Alice find work.",
    )


def test_observation_contains_contacts() -> None:
    npc = create_npc()
    social = create_social()
    memory = MemoryStore()

    social.send_message(
        sender_id="bob",
        recipient_id="alice",
        content="Hello Alice.",
        tick=1,
        intent=MessageIntent.GREETING,
    )

    builder = ObservationBuilder(
        job_board=create_job_board(),
        social=social,
        memory=memory,
    )

    observation = builder.build(
        npc=npc,
        tick=2,
    )

    assert observation.contacts == ("bob",)


def test_observation_contains_job_scores() -> None:
    job_board = JobBoard(
        [
            Job(
                id="easy-job",
                title="Easy Task",
                description="An easy task.",
                payment=1000.0,
                required_skills=["python"],
                difficulty=JobDifficulty.EASY,
            ),
            Job(
                id="hard-job",
                title="Hard Task",
                description="A hard task.",
                payment=3000.0,
                required_skills=["python"],
                difficulty=JobDifficulty.HARD,
            ),
        ]
    )
    npc = create_npc()
    social = SocialSystem(job_board=job_board)
    memory = MemoryStore()

    builder = ObservationBuilder(
        job_board=job_board,
        social=social,
        memory=memory,
    )

    observation = builder.build(
        npc=npc,
        tick=1,
    )
    scores = dict(observation.available_job_scores)

    assert scores["easy-job"] == 1000.0
    assert scores["hard-job"] == 3600.0


def test_observation_is_immutable() -> None:
    npc = create_npc()
    social = create_social()
    memory = MemoryStore()

    builder = ObservationBuilder(
        job_board=create_job_board(),
        social=social,
        memory=memory,
    )

    observation = builder.build(
        npc=npc,
        tick=1,
    )

    try:
        observation.goals = ()
    except AttributeError:
        pass
    else:
        raise AssertionError("Observation should be immutable")
