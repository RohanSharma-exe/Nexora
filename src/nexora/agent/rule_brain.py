"""Deterministic rule-based NPC brain."""

from nexora.agent.brain import Brain
from nexora.models.runtime import (
    ActionIntent,
    ActionType,
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
                reasoning="Progress an active goal using the highest-value available job.",
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

    @staticmethod
    def _best_job(observation: Observation) -> str | None:
        """Return the ID of the highest-scoring observed job."""

        if not observation.available_jobs:
            return None

        scores = dict(observation.available_job_scores)
        return max(
            observation.available_jobs,
            key=lambda job_id: scores.get(job_id, 0.0),
        )
