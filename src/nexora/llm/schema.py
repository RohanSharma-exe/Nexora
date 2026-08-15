"""Structured schema for model-generated NPC actions."""

from pydantic import BaseModel, ConfigDict, Field

from nexora.models.runtime import ActionType


class LLMAction(BaseModel):
    """Raw structured action returned by an LLM provider."""

    model_config = ConfigDict(extra="forbid")

    action: ActionType
    target_id: str | None
    content: str | None
    reasoning: str = Field()
