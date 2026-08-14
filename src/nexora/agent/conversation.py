from dataclasses import dataclass

from nexora.models.conversation import (
    ConversationMessage,
    MessageIntent,
)
from nexora.models.npc import NPC
from nexora.social import SocialSystem


@dataclass(frozen=True, slots=True)
class ConversationResponse:
    """Response generated from a message."""

    content: str
    intent: MessageIntent
    importance: float


class ConversationEngine:
    """Deterministic conversational reasoning for V0.4."""

    def respond(
        self,
        npc: NPC,
        message: ConversationMessage,
        social: SocialSystem,
    ) -> ConversationResponse:
        """Generate a contextual response."""

        text = message.content.lower()

        if message.intent == MessageIntent.THANKS or "thank" in text:
            return ConversationResponse(
                content="You're welcome!",
                intent=MessageIntent.REPLY,
                importance=0.4,
            )

        if "work" in text and (
            "?" in message.content
            or message.intent == MessageIntent.QUESTION
            or message.intent == MessageIntent.REQUEST
        ):
            suitable_jobs = []

            if social.job_board is not None:
                suitable_jobs = [
                    job for job in social.job_board.available() if job.is_suitable_for(npc.skills)
                ]

            if suitable_jobs:
                job = max(
                    suitable_jobs,
                    key=lambda item: item.payment,
                )

                return ConversationResponse(
                    content=(
                        f"I found a {job.title} paying "
                        f"₹{job.payment:.0f}. You might want to "
                        "check it out."
                    ),
                    intent=MessageIntent.OFFER,
                    importance=0.8,
                )

            return ConversationResponse(
                content=(
                    "I don't see any suitable work right now. "
                    "I'll let you know if I find something."
                ),
                intent=MessageIntent.REPLY,
                importance=0.7,
            )

        if (
            message.intent == MessageIntent.GREETING
            or "hello" in text
            or "hey" in text
            or "hi " in text
        ):
            return ConversationResponse(
                content=("Hey! Nice to hear from you. How's everything going?"),
                intent=MessageIntent.GREETING,
                importance=0.4,
            )

        return ConversationResponse(
            content=("Interesting. I'll keep that in mind."),
            intent=MessageIntent.REPLY,
            importance=0.3,
        )
