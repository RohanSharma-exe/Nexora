from dataclasses import dataclass

from nexora.agent.actions import Action, ActionType
from nexora.agent.scoring import UtilityScorer
from nexora.core.jobs import JobBoard
from nexora.models.npc import NPC


@dataclass(slots=True)
class Decision:
    """A selected action for an NPC."""

    action: str
    reason: str
    target_id: str | None = None
    score: float = 0.0


class DecisionEngine:
    """Selects actions using goals and personality."""

    def __init__(
        self,
        scorer: UtilityScorer | None = None,
    ) -> None:
        self.scorer = scorer or UtilityScorer()

    def decide(
        self,
        npc: NPC,
        job_board: JobBoard,
    ) -> Decision:
        incomplete_goals = [goal for goal in npc.goals if not goal.completed]

        if not incomplete_goals:
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
                reason=(f"No implemented strategy for '{goal.description}'."),
            )

        suitable_jobs = [job for job in job_board.available() if job.is_suitable_for(npc.skills)]

        if not suitable_jobs:
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

        best = max(
            scores,
            key=lambda score: score.score,
        )

        wait_score = self.scorer.score_wait(npc)

        if wait_score > best.score:
            return Decision(
                action=ActionType.WAIT.value,
                reason=(
                    f"Personality favors waiting. "
                    f"Wait score {wait_score:.2f} > "
                    f"best job score {best.score:.2f}."
                ),
                score=wait_score,
            )

        selected_job = job_board.get(best.job_id)

        return Decision(
            action=ActionType.COMPLETE_JOB.value,
            target_id=selected_job.id,
            reason=(
                f"Selected '{selected_job.title}' using utility "
                f"score {best.score:.2f}. "
                f"Payment ₹{selected_job.payment:.2f}, "
                f"risk penalty {best.risk_penalty:.2f}."
            ),
            score=best.score,
        )


def to_action(decision: Decision) -> Action:
    """Convert a decision into an executable action."""

    return Action(
        type=ActionType(decision.action),
        target_id=decision.target_id,
        reason=decision.reason,
    )
