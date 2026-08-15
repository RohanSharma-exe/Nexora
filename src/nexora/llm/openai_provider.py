"""OpenAI Responses API provider for Nexora NPC reasoning."""

from openai import OpenAI

from nexora.llm.provider import LLMProvider
from nexora.llm.schema import LLMAction
from nexora.models.runtime import ActionIntent, Observation


class OpenAILLMProvider(LLMProvider):
    """Generate structured NPC actions with the OpenAI Responses API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5-mini",
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def decide(self, observation: Observation) -> ActionIntent:
        """Generate and parse one structured NPC action."""

        response = self.client.responses.parse(
            model=self.model,
            input=self._prompt(observation),
            text_format=LLMAction,
        )

        action = response.output_parsed

        if action is None:
            raise RuntimeError("OpenAI returned no structured NPC action.")

        return ActionIntent(
            actor_id=observation.subject_id,
            action_type=action.action,
            target_id=action.target_id,
            payload=(
                {"content": action.content}
                if action.content is not None
                else {}
            ),
            reasoning=action.reasoning,
        )

    @staticmethod
    def _prompt(observation: Observation) -> str:
        """Serialize the observation into a compact decision prompt."""

        return (
            "You are the decision-making brain of an autonomous NPC in Nexora. "
            "Choose exactly one available action. Never invent targets or resources. "
            "Prefer actions that advance the NPC's active goals while respecting "
            "personality, risk tolerance, and current state.\n\n"
            f"NPC ID: {observation.subject_id}\n"
            f"Money: {observation.money:.2f}\n"
            f"Energy: {observation.energy:.2f}\n"
            f"Reputation: {observation.reputation:.2f}\n"
            f"Skills: {list(observation.skills)}\n"
            f"Personality: {dict(observation.personality)}\n"
            f"Goals: {list(observation.goals)}\n"
            f"Goal details: {[goal.model_dump() for goal in observation.goal_details]}\n"
            f"Memories: {list(observation.memories)}\n"
            f"Events: {list(observation.events)}\n"
            f"Contacts: {list(observation.contacts)}\n"
            f"Available actions: {list(observation.available_actions)}\n"
            f"Available jobs: {list(observation.available_jobs)}\n"
            f"Job scores: {dict(observation.available_job_scores)}\n"
            f"Job risks: {dict(observation.available_job_risks)}\n"
        )
