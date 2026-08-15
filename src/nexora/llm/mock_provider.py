"""Mock provider for exercising the LLM integration without an external API."""

from nexora.llm.provider import LLMProvider
from nexora.llm.schema import LLMAction
from nexora.models.runtime import ActionIntent, Observation


class MockLLMProvider(LLMProvider):
    """Provider backed by a predetermined structured action."""

    def __init__(self, action: LLMAction) -> None:
        self.action = action

    def decide(self, observation: Observation) -> ActionIntent:
        """Convert the configured structured response into an action intent."""

        return ActionIntent(
            actor_id=observation.subject_id,
            action_type=self.action.action,
            target_id=self.action.target_id,
            payload={
                "content": self.action.content,
            } if self.action.content is not None else {},
            reasoning=self.action.reasoning,
        )
