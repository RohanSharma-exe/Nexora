"""Deterministic provider used to validate the LLM provider contract."""

from nexora.agent.rule_brain import RuleBasedBrain
from nexora.llm.provider import LLMProvider
from nexora.models.runtime import ActionIntent, Observation


class RuleLLMProvider(LLMProvider):
    """Adapter that exposes the rule brain through the LLM provider interface."""

    def __init__(self) -> None:
        self._brain = RuleBasedBrain()

    def decide(self, observation: Observation) -> ActionIntent:
        """Delegate the decision to the deterministic rule brain."""

        return self._brain.decide(observation)
