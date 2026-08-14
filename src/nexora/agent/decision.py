from dataclasses import dataclass

from nexora.agent.actions import Action, ActionType
from nexora.agent.scoring import UtilityScorer
from nexora.core.jobs import JobBoard
from nexora.models.npc import NPC
from nexora.social import SocialSystem


@dataclass(slots=True)
class Decision:
    """A selected action for an NPC."""

    action: str
    reason: str
    target_id: str | None = None
    content: str | None = None
    score: float = 0.0


class DecisionEngine:
    """Selects actions using goals, personality, and social state."""

    def __init__(
        self,
        scorer: UtilityScorer | None = None,
    ) -> None:
        self.scorer = scorer or UtilityScorer()

    def decide(
        self,
        npc: NPC,
        job_board: JobBoard,
        social: SocialSystem | None = None,
    ) -> Decision:
        """Select the next action for an NPC."""
        if social is None:
            social = SocialSystem()
            social.register_npc(npc.id)

        incomplete_goals = [goal for goal in npc.goals if not goal.completed]
        contacts = social.contacts(npc.id)
        unread = social.unread_count(npc.id)

        if unread > 0 and contacts:
            contact = contacts[-1]
            social_score = npc.personality.sociability * 0.75

            if social_score >= 0.45:
                return Decision(
                    action=ActionType.SEND_MESSAGE.value,
                    target_id=contact,
                    content=f"Hey, {contact}. How are things going?",
                    reason=(
                        f"{npc.name}'s sociability motivates social interaction."
                    ),
                    score=social_score,
                )

        if not contacts and npc.personality.sociability >= 0.6:
            contact = social.suggest_contact(npc.id)

            if contact is not None:
                social_score = npc.personality.sociability
                return Decision(
                    action=ActionType.SEND_MESSAGE.value,
                    target_id=contact,
                    content=(
                        f"Hey {contact}, I'm {npc.name}. "
                        "What are you working on?"
                    ),
                    reason=(
                        "The NPC has no contacts and enough sociability "
                        "to initiate a new interaction."
                    ),
                    score=social_score,
                )

        if not incomplete_goals:
            if contacts and npc.personality.sociability >= 0.5:
                contact = contacts[0]
                return Decision(
                    action=ActionType.SEND_MESSAGE.value,
                    target_id=contact,
                    content=f"Hey {contact}, want to catch up?",
                    reason=(
                        "No active goals remain, so the NPC prioritizes "
                        "social interaction."
                    ),
                    score=npc.personality.sociability,
                )

            return Decision(
                action=ActionType.IDLE.value,
                reason="The NPC has no incomplete goals.",
            )

        goal = max(
            incomplete_goals,
            key=lambda item: item.priority,
        )

        if "earn" not in goal.description.lower():
            return Decision(
                action=ActionType.IDLE.value,
                reason=f"No implemented strategy for '{goal.description}'.",
            )

        suitable_jobs = [
            job
            for job in job_board.available()
            if job.is_suitable_for(npc.skills)
        ]

        if not suitable_jobs:
            if contacts and npc.personality.sociability >= 0.6:
                contact = contacts[0]
                return Decision(
                    action=ActionType.SEND_MESSAGE.value,
                    target_id=contact,
                    content=(
                        "I couldn't find suitable work. "
                        "Do you know of anything available?"
                    ),
                    reason=(
                        "No suitable jobs are available, so the NPC seeks "
                        "help from a contact."
                    ),
                    score=0.6,
                )

            return Decision(
                action=ActionType.WAIT.value,
                reason="No suitable jobs are currently available.",
            )

        maximum_payment = max(job.payment for job in suitable_jobs)
        scores = [
            self.scorer.score_job(
                npc=npc,
                job=job,
                maximum_payment=maximum_payment,
            )
            for job in suitable_jobs
        ]

        best = max(scores, key=lambda score: score.score)
        wait_score = self.scorer.score_wait(npc)

        if wait_score > best.score:
            return Decision(
                action=ActionType.WAIT.value,
                reason=(
                    f"Personality favors waiting. Wait score "
                    f"{wait_score:.2f} > best job score {best.score:.2f}."
                ),
                score=wait_score,
            )

        selected_job = job_board.get(best.job_id)

        return Decision(
            action=ActionType.COMPLETE_JOB.value,
            target_id=selected_job.id,
            reason=(
                f"Selected '{selected_job.title}' using utility "
                f"score {best.score:.2f}. Payment ₹{selected_job.payment:.2f}, "
                f"risk penalty {best.risk_penalty:.2f}."
            ),
            score=best.score,
        )


def to_action(decision: Decision) -> Action:
    """Convert a decision into an executable action."""

    return Action(
        type=ActionType(decision.action),
        target_id=decision.target_id,
        content=decision.content,
        reason=decision.reason,
    )
