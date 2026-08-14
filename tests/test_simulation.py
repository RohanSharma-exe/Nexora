from nexora.core.world import World
from nexora.models.job import Job
from nexora.models.npc import NPC, Goal
from nexora.simulation.engine import SimulationEngine


def test_one_engine_tick_executes_agents_once() -> None:
    world = World()

    world.add_npc(
        NPC(
            id="alice",
            name="Alice",
            occupation="Developer",
            skills=["python"],
            goals=[
                Goal(
                    description="Earn ₹5000",
                    priority=0.9,
                    target_amount=5000,
                )
            ],
        )
    )

    world.add_job(
        Job(
            id="job-1",
            title="Python Job",
            description="Write Python code.",
            payment=2000,
            required_skills=["python"],
        )
    )

    engine = SimulationEngine(world)

    results = engine.tick()

    assert len(results) == 1
    assert results[0].decision.action == "complete_job"
    assert world.get_npc("alice").money == 3000
    assert world.hour == 10
    assert world.tick_count == 1
