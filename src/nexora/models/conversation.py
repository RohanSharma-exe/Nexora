from enum import StrEnum

from pydantic import BaseModel, Field


class MessageIntent(StrEnum):
    """Intent expressed by an NPC message."""

    GREETING = "greeting"
    QUESTION = "question"
    REQUEST = "request"
    OFFER = "offer"
    THANKS = "thanks"
    REPLY = "reply"
    CASUAL = "casual"


class ConversationMessage(BaseModel):
    """A persistent conversational message."""

    id: int
    sender_id: str
    recipient_id: str
    content: str
    intent: MessageIntent
    tick: int
    processed: bool = False


class ConversationMemory(BaseModel):
    """Persistent memory of an interaction."""

    message_id: int
    npc_id: str
    other_npc_id: str
    summary: str
    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )
