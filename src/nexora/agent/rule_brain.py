"""Deterministic rule-based NPC brain."""

from nexora.agent.brain import Brain
from nexora.models.runtime import (
    ActionIntent,
    ActionType,
    GoalObservation,
    Observation,
)


class RuleBasedBrain(Brain):
    """Make deterministic decisions using the NPC observation."""

    def decide(self, observation: Observation) -> ActionIntent:
        """Select the highest-priority action available to the NPC."""

        actions = set(observation.available_actions)

        if observation.events and "send_message" in actions:
            return ActionIntent(
                actor_id=observation.subject_id,
                action_type=ActionType.SEND_MESSAGE,
                target_id=(observation.contacts[0] if observation.contacts else None),
                reasoning="Respond to an incoming event.",
            )

        if observation.goals and "complete_job" in actions:
            target_id = self._best_job(observation)

            return ActionIntent(
                actor_id=observation.subject_id,
                action_type=ActionType.COMPLETE_JOB,
                target_id=target_id,
                reasoning=self._job_reason(observation, target_id),
            )

        if "wait" in actions:
            return ActionIntent(
                actor_id=observation.subject_id,
                action_type=ActionType.WAIT,
                reasoning="No higher-priority action is currently available.",
            )

        return ActionIntent(
            actor_id=observation.subject_id,
            action_type=ActionType.IDLE,
            reasoning="No actionable behavior is available.",
        )

    @classmethod
    def _best_job(cls, observation: Observation) -> str | None:
        """Return the job with the highest personality-aware utility."""

        if not observation.available_jobs:
            return None

        scores = dict(observation.available_job_scores)
        risks = dict(observation.available_job_risks)
        goal = cls._primary_goal(observation.goal_details)
        traits = dict(observation.personality)

        ambition = traits.get("ambition", 0.5)
        greed = traits.get("greed", 0.5)
        risk_tolerance = traits.get("risk_tolerance", 0.5)
        patience = traits.get("patience", 0.5)

        goal_priority = goal.priority if goal is not None else 0.5
        progress_ratio = cls._goal_progress_ratio(goal)
        urgency = (
            goal_priority * 0.30
            + ambition * 0.20
            + greed * 0.20
            + (1.0 - progress_ratio) * 0.20
            + (1.0 - patience) * 0.10
        )

        def utility(job_id: str) -> float:
            base_score = scores.get(job_id, 0.0)
            job_risk = risks.get(job_id, 0.5)
            risk_distance = abs(job_risk - risk_tolerance)

            value_component = base_score * (
                0.50
                + 0.20 * greed
                + 0.15 * ambition
            )
            urgency_component = urgency * 500.0
            risk_component = -risk_distance * 5000.0

            return (
                value_component
                + urgency_component
                + risk_component
            )

        return max(observation.available_jobs, key=utility)

    @staticmethod
    def _primary_goal(
        goals: tuple[GoalObservation, ...],
    ) -> GoalObservation | None:
        if not goals:
            return None

        return max(goals, key=lambda goal: goal.priority)

    @staticmethod
    def _goal_progress_ratio(
        goal: GoalObservation | None,
    ) -> float:
        if goal is None or goal.target_amount in (None, 0.0):
            return 0.0

        return min(goal.progress / goal.target_amount, 1.0)

    @staticmethod
    def _job_reason(
        observation: Observation,
        job_id: str | None,
    ) -> str:
        if job_id is None:
            return "No actionable job target was available."

        goal = RuleBasedBrain._primary_goal(observation.goal_details)
        goal_text = goal.description if goal is not None else "an active goal"
        traits = dict(observation.personality)
        risk = dict(observation.available_job_risks).get(job_id, 0.5)

        return (
            f"Selected '{job_id}' to progress {goal_text}; "
            f"ambition={traits.get('ambition', 0.5):.2f}, "
            f"greed={traits.get('greed', 0.5):.2f}, "
            f"risk_tolerance={traits.get('risk_tolerance', 0.5):.2f}, "
            f"job_risk={risk:.2f}."
        )
