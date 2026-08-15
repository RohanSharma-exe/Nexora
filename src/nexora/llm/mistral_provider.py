"""Mistral-hosted LLM provider."""

import os
from typing import Any

from mistralai import Mistral

from nexora.llm.prompt import SYSTEM_PROMPT, build_decision_prompt
from nexora.llm.provider import LLMProvider
from nexora.llm.schema import LLMAction
from nexora.models.runtime import ActionIntent, Observation


class MistralProvider(LLMProvider):
    """Use Mistral custom structured outputs for NPC action decisions."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        key = api_key or os.getenv("MISTRAL_API_KEY")
        if not key:
            raise ValueError("MISTRAL_API_KEY is not configured.")

        self.model = model or os.getenv("MISTRAL_MODEL", "mistral-large-latest")
        self.client = client or Mistral(api_key=key)

    def decide(self, observation: Observation) -> ActionIntent:
        """Generate and validate one structured NPC action."""

        response = self.client.chat.complete(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_decision_prompt(observation)},
            ],
            temperature=0,
            response_format=LLMAction,
        )

        content = response.choices[0].message.content
        if not isinstance(content, str) or not content:
            raise ValueError("Mistral returned an empty response.")

        action = LLMAction.model_validate_json(content)
        payload = {"content": action.content} if action.content is not None else {}

        return ActionIntent(
            actor_id=observation.subject_id,
            action_type=action.action,
            target_id=action.target_id,
            payload=payload,
            reasoning=action.reasoning,
        )
