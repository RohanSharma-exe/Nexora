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
                reasoning="Respond to an incoming event.",
            )

        if observation.goals and "complete_job" in actions:
            return ActionIntent(
                actor_id=observation.subject_id,
                action_type=ActionType.COMPLETE_JOB,
                reasoning="Progress an active goal.",
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
