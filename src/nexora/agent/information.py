from dataclasses import dataclass

from nexora.models.information import Information
from nexora.models.npc import NPC
from nexora.models.relationship import Relationship


@dataclass(frozen=True)
class SharingDecision:
    should_share: bool
    score: float
    reason: str


class InformationSharingEngine:
    """Decides whether an NPC should share useful information."""

    def decide(
        self,
        npc: NPC,
        recipient: NPC,
        relationship: Relationship,
        information: Information,
    ) -> SharingDecision:
        trust = relationship.trust
        familiarity = relationship.familiarity

        benefit = min(max(information.value, 0.0), 1.0)

        cooperation = (
            trust * 0.35
            + familiarity * 0.15
            + npc.personality.sociability * 0.15
            + npc.personality.curiosity * 0.10
            + npc.reputation * 0.15
        )

        greed_penalty = npc.personality.greed * 0.15

        competition_penalty = 0.0

        if information.type.value == "job":
            competition_penalty = npc.personality.greed * 0.10

        score = cooperation + benefit * 0.20 - greed_penalty - competition_penalty

        score = max(0.0, min(1.0, score))

        if score >= 0.50:
            return SharingDecision(
                should_share=True,
                score=score,
                reason=(
                    f"{npc.name} chose to share '{information.title}' "
                    f"because the relationship and expected benefit "
                    f"outweigh the cost of sharing."
                ),
            )

        return SharingDecision(
            should_share=False,
            score=score,
            reason=(
                f"{npc.name} kept '{information.title}' private "
                f"because the sharing score was too low."
            ),
        )
