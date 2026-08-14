from nexora.core.world import World
from nexora.models.job import Job
from nexora.models.npc import NPC


def create_world() -> World:
    world = World()

    world.add_npc(
        NPC(
            id="alice",
            name="Alice",
            occupation="Developer",
        )
    )

    return world


def test_world_can_add_npc() -> None:
    world = create_world()

    assert world.get_npc("alice").name == "Alice"


def test_world_can_add_job() -> None:
    world = create_world()

    world.add_job(
        Job(
            id="job-1",
            title="Python Developer",
            description="Build an API.",
            payment=2000,
            required_skills=["python"],
        )
    )

    assert len(world.job_board.available()) == 1


def test_world_time_advances() -> None:
    world = create_world()

    world.advance_time()

    assert world.hour == 10
    assert world.day == 1


def test_world_rolls_over_to_next_day() -> None:
    world = World(
        day=1,
        hour=23,
    )

    world.add_npc(
        NPC(
            id="alice",
            name="Alice",
            occupation="Developer",
        )
    )

    world.advance_time()

    assert world.hour == 0
    assert world.day == 2
