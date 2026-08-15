from nexora.agent.rule_brain import RuleBasedBrain
from nexora.cli import create_demo_world
from nexora.simulation.engine import SimulationEngine, create_brain


def test_create_rule_brain() -> None:
    brain = create_brain("rule")

    assert isinstance(brain, RuleBasedBrain)


def test_unknown_brain_is_rejected() -> None:
    try:
        create_brain("unknown")
    except ValueError as exc:
        assert "Unknown brain" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_rule_brain_runs_one_simulation_tick() -> None:
    world = create_demo_world()

    engine = SimulationEngine(
        world,
        brain=RuleBasedBrain(),
    )

    results = engine.tick()

    assert len(results) == 3
    assert world.tick_count == 1


def test_rule_brain_progresses_goal() -> None:
    world = create_demo_world()

    engine = SimulationEngine(
        world,
        brain=RuleBasedBrain(),
    )

    engine.tick()

    alice = world.get_npc("alice")

    assert alice.money > 1000.0
    assert alice.goals[0].progress > 0.0
