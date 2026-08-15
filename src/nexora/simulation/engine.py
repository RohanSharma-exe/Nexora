from nexora.agent.agent import AgentResult
from nexora.agent.brain import Brain
from nexora.agent.rule_brain import RuleBasedBrain
from nexora.core.world import World
from nexora.llm.brain import LLMBrain
from nexora.llm.gemini_provider import GeminiProvider
from nexora.llm.groq_provider import GroqProvider
from nexora.llm.mistral_provider import MistralProvider
from nexora.llm.nvidia_provider import NVIDIAProvider
from nexora.llm.rule_provider import RuleLLMProvider


class SimulationEngine:
    """Runs the Nexora world."""

    def __init__(
        self,
        world: World,
        brain: Brain | None = None,
    ) -> None:
        self.world = world
        self.brain = brain

        if self.brain is not None:
            for agent in self.world.agents.values():
                agent.brain = self.brain

    def tick(self) -> list[AgentResult]:
        """Run exactly one simulation tick."""

        self.world.tick_count += 1

        results: list[AgentResult] = []

        for agent in self.world.agents.values():
            if self.brain is None:
                results.append(
                    agent.tick(
                        current_tick=self.world.tick_count,
                    )
                )
            else:
                results.append(
                    agent.act_with_brain(
                        current_tick=self.world.tick_count,
                    )
                )

        self.world.advance_time()

        return results

    def run(
        self,
        ticks: int = 1,
    ) -> list[list[AgentResult]]:
        """Run the simulation for multiple ticks."""

        return [self.tick() for _ in range(ticks)]


def create_brain(name: str) -> Brain:
    """Create a supported brain implementation."""

    if name == "rule":
        return RuleBasedBrain()
    if name == "rule-llm":
        return LLMBrain(RuleLLMProvider())
    if name == "nvidia":
        return LLMBrain(NVIDIAProvider())
    if name == "gemini":
        return LLMBrain(GeminiProvider())
    if name == "groq":
        return LLMBrain(GroqProvider())
    if name == "mistral":
        return LLMBrain(MistralProvider())

    supported = "rule, rule-llm, nvidia, gemini, groq, mistral"
    raise ValueError(f"Unknown brain '{name}'. Supported brains: {supported}")
