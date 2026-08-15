"""Provider abstraction for language-model-backed NPC brains."""

from abc import ABC, abstractmethod

from nexora.models.runtime import ActionIntent, Observation


class LLMProvider(ABC):
    """Interface implemented by concrete LLM providers."""

    @abstractmethod
    def decide(self, observation: Observation) -> ActionIntent:
        """Generate one validated NPC action intent from an observation."""
        raise NotImplementedError
