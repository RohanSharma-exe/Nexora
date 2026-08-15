"""Provider-backed NPC brain."""

from nexora.agent.brain import Brain
from nexora.llm.provider import LLMProvider
from nexora.models.runtime import ActionIntent, ActionType, Observation


class LLMBrain(Brain):
    """Delegate NPC reasoning to a provider behind the Brain interface."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def decide(self, observation: Observation) -> ActionIntent:
        """Generate one action intent from the current observation."""

        intent = self._repair_intent(observation, self.provider.decide(observation))
        self._validate_intent(observation, intent)
        return intent

    @staticmethod
    def _repair_intent(
        observation: Observation,
        intent: ActionIntent,
    ) -> ActionIntent:
        """Repair a missing job target using deterministic observed job scores.

        Providers can occasionally return a structurally valid action with a null
        target even when a target is required. We only repair a missing job target;
        invented or unavailable targets are still rejected by validation.
        """

        if (
            intent.action_type == ActionType.COMPLETE_JOB
            and intent.target_id is None
            and observation.available_jobs
        ):
            scores = dict(observation.available_job_scores)
            target_id = max(
                observation.available_jobs,
                key=lambda job_id: scores.get(job_id, float("-inf")),
            )
            reasoning = intent.reasoning.strip()
            fallback_reason = (
                f"Provider omitted a job target; selected '{target_id}' "
                "using the highest observed job score."
            )
            return ActionIntent(
                actor_id=intent.actor_id,
                action_type=intent.action_type,
                target_id=target_id,
                payload=intent.payload,
                reasoning=f"{reasoning} {fallback_reason}".strip(),
            )

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
