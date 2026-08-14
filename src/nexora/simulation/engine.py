from nexora.agent.agent import AgentResult
from nexora.core.world import World


class SimulationEngine:
    """Runs the Nexora world."""

    def __init__(self, world: World) -> None:
        self.world = world

    def tick(self) -> list[AgentResult]:
        """Run exactly one simulation tick."""

        self.world.tick_count += 1

        results: list[AgentResult] = []

        for agent in self.world.agents.values():
            results.append(
                agent.tick(
                    current_tick=self.world.tick_count,
                )
            )

        self.world.advance_time()

        return results

    def run(self, ticks: int = 1) -> list[list[AgentResult]]:
        """Run the simulation for multiple ticks."""

        return [self.tick() for _ in range(ticks)]
