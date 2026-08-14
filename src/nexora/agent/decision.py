from dataclasses import dataclass

from nexora.agent.actions import Action, ActionType
from nexora.core.jobs import JobBoard
from nexora.models.npc import NPC


@dataclass(slots=True)
class Decision:
    """A selected action for an NPC."""

    action: str
    reason: str
    target_id: str | None = None


class DecisionEngine:
    """Produces actions from the NPC and world state."""

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

        if "earn" in goal.description.lower():
            suitable_jobs = [
                job for job in job_board.available() if job.is_suitable_for(npc.skills)
            ]

            if not suitable_jobs:
                return Decision(
                    action=ActionType.REST.value,
                    reason=(
                        "There are no suitable jobs available. "
                        "The NPC will rest before trying again."
                    ),
                )

            best_job = max(
                suitable_jobs,
                key=lambda job: job.payment,
            )

            return Decision(
                action=ActionType.COMPLETE_JOB.value,
                target_id=best_job.id,
                reason=(
                    f"The highest-priority goal is '{goal.description}'. "
                    f"The best available opportunity is "
                    f"'{best_job.title}' paying ₹{best_job.payment:.2f}."
                ),
            )

        return Decision(
            action=ActionType.IDLE.value,
            reason=(
                f"The highest-priority goal is "
                f"'{goal.description}', but no action "
                "is currently implemented for it."
            ),
        )


def to_action(decision: Decision) -> Action:
    """Convert a decision into an executable action."""

    return Action(
        type=ActionType(decision.action),
        target_id=decision.target_id,
        reason=decision.reason,
    )
