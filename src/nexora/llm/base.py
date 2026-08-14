from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface implemented by every LLM provider."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from a prompt."""
        raise NotImplementedError
