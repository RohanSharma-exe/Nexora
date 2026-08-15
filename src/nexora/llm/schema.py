"""Structured schema for model-generated NPC actions."""

from pydantic import BaseModel, Field

from nexora.models.runtime import ActionType


class LLMAction(BaseModel):
    """Raw structured action returned by an LLM provider."""

    action: ActionType
    target_id: str | None = None
    content: str | None = None
    reasoning: str = Field(default="")
