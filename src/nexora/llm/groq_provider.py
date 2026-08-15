"""Groq-hosted LLM provider."""

import os

from nexora.llm.openai_compatible import OpenAICompatibleLLMProvider


class GroqProvider(OpenAICompatibleLLMProvider):
    """Use Groq's OpenAI-compatible inference API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY is not configured.")

        selected_model = model or os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"

        super().__init__(
            api_key=key,
            base_url="https://api.groq.com/openai/v1",
            model=selected_model,
        )
