from dataclasses import dataclass

from nexora.agent.actions import (
    Action,
    ActionExecutor,
    ActionResult,
    ActionType,
)
from nexora.agent.brain import Brain
from nexora.agent.conversation import (
    ConversationEngine,
    ConversationResponse,
)
from nexora.agent.decision import (
    Decision,
    DecisionEngine,
    to_action,
)
from nexora.agent.observation import ObservationBuilder
from nexora.core.jobs import JobBoard
from nexora.memory.memory import MemoryStore
from nexora.models.conversation import (
    ConversationMessage,
    MessageIntent,
)
from nexora.models.npc import NPC
from nexora.models.runtime import ActionIntent, Observation
from nexora.social import SocialSystem


@dataclass(slots=True)
class AgentResult:
    """Result of one agent tick."""

    npc_id: str
    decision: Decision
    result: ActionResult


class Agent:
    """Autonomous controller operating an NPC."""

    def __init__(
        self,
        npc: NPC,
        job_board: JobBoard,
        social: SocialSystem,
        memory: MemoryStore | None = None,
        decision_engine: DecisionEngine | None = None,
        brain: Brain | None = None,
    ) -> None:
        self.npc = npc
        self.job_board = job_board
        self.social = social
        self.memory = memory or MemoryStore()
        self.decision_engine = decision_engine or DecisionEngine()
        self.conversation_engine = ConversationEngine()
        self.observation_builder = ObservationBuilder(
            job_board=self.job_board,
            social=self.social,
            memory=self.memory,
        )
        self.brain = brain

    def observe(self) -> str:
        """Create the legacy string representation of NPC state."""

        goals = [goal.description for goal in self.npc.goals if not goal.completed]

        jobs = [
            job.title for job in self.job_board.available() if job.is_suitable_for(self.npc.skills)
        ]

        return (
            f"Name: {self.npc.name}\n"
            f"Occupation: {self.npc.occupation}\n"
            f"Money: {self.npc.money:.2f}\n"
            f"Energy: {self.npc.energy:.2f}\n"
            f"Reputation: {self.npc.reputation:.2f}\n"
            f"Goals: {goals}\n"
            f"Suitable jobs: {jobs}\n"
            f"Contacts: {self.social.contacts(self.npc.id)}\n"
            f"Unread messages: {self.social.unread_count(self.npc.id)}"
        )

    def observe_structured(
        self,
        current_tick: int = 0,
    ) -> Observation:
        """Build the structured observation used by brains."""

        return self.observation_builder.build(
            npc=self.npc,
            tick=current_tick,
        )

    def decide(self, current_tick: int = 0) -> Decision:
        """Choose the next action using the legacy decision engine."""

        return self.decision_engine.decide(
            self.npc,
            self.job_board,
            self.social,
            current_tick=current_tick,
        )

    def decide_with_brain(
        self,
        current_tick: int = 0,
    ) -> ActionIntent:
        """Choose the next action through the configured brain."""

        if self.brain is None:
            raise RuntimeError("No brain is configured for this agent.")

        observation = self.observe_structured(
            current_tick=current_tick,
        )

        return self.brain.decide(observation)

    def _has_active_goal(self) -> bool:
        """Return whether the NPC has an incomplete goal."""

        return any(not goal.completed for goal in self.npc.goals)

    def _apply_conversation_consequence(
        self,
        message: ConversationMessage,
        response: ConversationResponse,
    ) -> None:
        """Update relationships and reputation based on an interaction."""

        if response.intent == MessageIntent.OFFER:
            self.social.apply_relationship_outcome(
                source_id=message.sender_id,
                target_id=self.npc.id,
                trust_delta=0.08,
                respect_delta=0.05,
                familiarity_delta=0.02,
            )

            self.social.adjust_reputation(
                npc_id=self.npc.id,
                delta=0.05,
            )

            return

        if response.intent == MessageIntent.REPLY:
            self.social.apply_relationship_outcome(
                source_id=message.sender_id,
                target_id=self.npc.id,
                familiarity_delta=0.02,
            )

            return

        if response.intent == MessageIntent.GREETING:
            self.social.apply_relationship_outcome(
                source_id=message.sender_id,
                target_id=self.npc.id,
                familiarity_delta=0.02,
            )

    def process_message(
        self,
        current_tick: int,
    ) -> ActionResult | None:
        """Process one incoming message when socially appropriate."""

        if self._has_active_goal():
            return None

        messages = self.social.inbox(
            self.npc.id,
            unprocessed_only=True,
        )

        if not messages:
            return None

        message = messages[0]

        if not self.social.can_message(
            self.npc.id,
            message.sender_id,
            current_tick,
        ):
            return None

        response = self.conversation_engine.respond(
            npc=self.npc,
            message=message,
            job_board=self.job_board,
        )

        self._apply_conversation_consequence(
            message=message,
            response=response,
        )

        self.social.process_message(
            npc_id=self.npc.id,
            message_id=message.id,
        )

        self.social.remember(
            message=message,
            npc_id=self.npc.id,
            summary=(f"{message.sender_id} said: {message.content}"),
            importance=response.importance,
        )

        executor = ActionExecutor(
            job_board=self.job_board,
            memory=self.memory,
            social=self.social,
            current_tick=current_tick,
        )

        return executor.execute(
            npc=self.npc,
            action=Action(
                type=ActionType.SEND_MESSAGE,
                target_id=message.sender_id,
                content=response.content,
                intent=response.intent,
            ),
        )

    def _decision_from_intent(
        self,
        intent: ActionIntent,
    ) -> Decision:
        """Convert a brain intent into the existing decision model."""

        return Decision(
            action=intent.action_type.value,
            target_id=intent.target_id,
            content=intent.payload.get("content"),
            reason=intent.reasoning,
            score=0.0,
        )

    def act(
        self,
        decision: Decision,
        current_tick: int = 0,
    ) -> ActionResult:
        """Execute the selected action."""

        action = to_action(decision)

        executor = ActionExecutor(
            job_board=self.job_board,
            memory=self.memory,
            social=self.social,
            current_tick=current_tick,
        )

        return executor.execute(
            npc=self.npc,
            action=action,
        )

    def act_with_brain(
        self,
        current_tick: int = 0,
    ) -> AgentResult:
        """Run one brain-driven action without changing the legacy path."""

        intent = self.decide_with_brain(
            current_tick=current_tick,
        )

        decision = self._decision_from_intent(intent)

        result = self.act(
            decision,
            current_tick=current_tick,
        )

        self.update_goals(result)

        return AgentResult(
            npc_id=self.npc.id,
            decision=decision,
            result=result,
        )

    def update_goals(self, result: ActionResult) -> None:
        """Update goal progress after an action."""

        if not result.success or result.money_change <= 0:
            return

        for goal in self.npc.goals:
            if goal.completed:
                continue

            if goal.target_amount is None:
                continue

            goal.add_progress(
                result.money_change,
            )

            if goal.completed:
                self.memory.add(
                    content=(
                        f"Goal completed: {goal.description}. Progress: ₹{goal.progress:.2f}."
                    ),
                    importance=1.0,
                )

    def tick(
        self,
        current_tick: int = 0,
    ) -> AgentResult:
        """Run one autonomous cycle using the legacy decision path."""

        incoming = self.process_message(
            current_tick=current_tick,
        )

        if incoming is not None:
            decision = Decision(
                action=ActionType.SEND_MESSAGE.value,
                reason="Processed an incoming message.",
            )

            return AgentResult(
                npc_id=self.npc.id,
                decision=decision,
                result=incoming,
            )

        self.observe()

        decision = self.decide(
            current_tick=current_tick,
        )

        result = self.act(
            decision,
            current_tick=current_tick,
        )

        self.update_goals(result)

        return AgentResult(
            npc_id=self.npc.id,
            decision=decision,
            result=result,
        )
