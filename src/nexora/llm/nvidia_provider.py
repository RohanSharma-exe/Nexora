"""NVIDIA-hosted LLM provider."""

import os

from nexora.llm.openai_compatible import OpenAICompatibleLLMProvider


class NVIDIAProvider(OpenAICompatibleLLMProvider):
    """Use NVIDIA's OpenAI-compatible hosted inference API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        key = api_key or os.getenv("NVIDIA_API_KEY")
        if not key:
            raise ValueError("NVIDIA_API_KEY is not configured.")

        selected_model = model or os.getenv("NVIDIA_MODEL")
        if not selected_model:
            raise ValueError("NVIDIA_MODEL is not configured.")

        super().__init__(
            api_key=key,
            base_url="https://integrate.api.nvidia.com/v1",
            model=selected_model,
        )
