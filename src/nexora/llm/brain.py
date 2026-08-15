"""Provider-backed NPC brain."""

from nexora.agent.brain import Brain
from nexora.llm.provider import LLMProvider
from nexora.models.runtime import ActionIntent, Observation


class LLMBrain(Brain):
    """Delegate NPC reasoning to a provider behind the Brain interface."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def decide(self, observation: Observation) -> ActionIntent:
        """Generate one action intent from the current observation."""

        intent = self.provider.decide(observation)
        self._validate_intent(observation, intent)
        return intent

    @staticmethod
    def _validate_intent(
        observation: Observation,
        intent: ActionIntent,
    ) -> None:
        """Reject actions that target actors or resources outside the observation."""

        if intent.actor_id != observation.subject_id:
            raise ValueError("LLM intent actor does not match the observation subject.")

        if intent.action_type.value not in observation.available_actions:
            raise ValueError(f"Action '{intent.action_type.value}' is not currently available.")

        if intent.action_type.value == "complete_job":
            if intent.target_id not in observation.available_jobs:
                raise ValueError(f"Job '{intent.target_id}' is not available to this NPC.")

        if intent.action_type.value == "send_message":
            if intent.target_id not in observation.contacts:
                raise ValueError(f"Contact '{intent.target_id}' is not known to this NPC.")
