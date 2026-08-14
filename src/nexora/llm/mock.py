from nexora.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Deterministic LLM substitute used during V0 development."""

    def generate(self, prompt: str) -> str:
        del prompt
        return "continue_goal"
