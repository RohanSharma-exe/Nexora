"""Interfaces for NPC decision-making brains."""

from abc import ABC, abstractmethod

from nexora.models.runtime import ActionIntent, Observation


class Brain(ABC):
    """Interface implemented by every NPC decision-making strategy."""

    @abstractmethod
    def decide(self, observation: Observation) -> ActionIntent:
        """Choose the next action from the current observation."""
        raise NotImplementedError
