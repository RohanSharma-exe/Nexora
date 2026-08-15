"""Provider for OpenAI-compatible hosted LLM APIs."""

import json
from typing import Any

from openai import OpenAI

from nexora.llm.prompt import SYSTEM_PROMPT, build_decision_prompt
from nexora.llm.provider import LLMProvider
from nexora.llm.schema import LLMAction
from nexora.models.runtime import ActionIntent, Observation


class OpenAICompatibleLLMProvider(LLMProvider):
    """Call an OpenAI-compatible endpoint and validate its structured action."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.client = client or OpenAI(api_key=api_key, base_url=base_url, timeout=120.0)

    def decide(self, observation: Observation) -> ActionIntent:
        """Generate and validate one structured NPC action."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_decision_prompt(observation)},
            ],
            temperature=0,
            max_completion_tokens=512,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "nexora_action",
                    "strict": True,
                    "schema": LLMAction.model_json_schema(),
                },
            },
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM provider returned an empty response.")

        action = LLMAction.model_validate(json.loads(content))
        payload = {"content": action.content} if action.content is not None else {}

        return ActionIntent(
            actor_id=observation.subject_id,
            action_type=action.action,
            target_id=action.target_id,
            payload=payload,
            reasoning=action.reasoning,
        )
