"""Google Gemini LLM provider."""

import os
from typing import Any

from google import genai
from google.genai import types

from nexora.llm.prompt import SYSTEM_PROMPT, build_decision_prompt
from nexora.llm.provider import LLMProvider
from nexora.llm.schema import LLMAction
from nexora.models.runtime import ActionIntent, Observation


class GeminiProvider(LLMProvider):
    """Use Gemini structured output for NPC action decisions."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        selected_model = model or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
        self.model: str = selected_model
        self.client = client or genai.Client(api_key=key)

    def decide(self, observation: Observation) -> ActionIntent:
        """Generate and validate one structured NPC action."""

        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{SYSTEM_PROMPT}\n\n{build_decision_prompt(observation)}",
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=LLMAction,
            ),
        )

        content = response.text
        if not content:
            raise ValueError("Gemini returned an empty response.")

        action = LLMAction.model_validate_json(content)
        payload = {"content": action.content} if action.content is not None else {}

        return ActionIntent(
            actor_id=observation.subject_id,
            action_type=action.action,
            target_id=action.target_id,
            payload=payload,
            reasoning=action.reasoning,
        )
