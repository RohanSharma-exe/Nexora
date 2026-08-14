from dataclasses import dataclass

from nexora.agent.actions import (
    Action,
    ActionExecutor,
    ActionResult,
    ActionType,
)
from nexora.agent.conversation import ConversationEngine
from nexora.agent.decision import Decision, DecisionEngine, to_action
from nexora.core.jobs import JobBoard
from nexora.memory.memory import MemoryStore
from nexora.models.npc import NPC
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
    ) -> None:
        self.npc = npc
        self.job_board = job_board
        self.social = social
        self.memory = memory or MemoryStore()
        self.decision_engine = decision_engine or DecisionEngine()
        self.conversation_engine = ConversationEngine()

    def observe(self) -> str:
        """Create a representation of the NPC's current state."""

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

    def decide(self) -> Decision:
        """Choose the next action."""

        return self.decision_engine.decide(
            self.npc,
            self.job_board,
            self.social,
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

    def update_goals(self, result: ActionResult) -> None:
        """Update goal progress after an action."""

        if not result.success or result.money_change <= 0:
            return

        for goal in self.npc.goals:
            if goal.completed:
                continue

            if goal.target_amount is None:
                continue

            goal.add_progress(result.money_change)

            if goal.completed:
                self.memory.add(
                    content=(
                        f"Goal completed: {goal.description}. Progress: ₹{goal.progress:.2f}."
                    ),
                    importance=1.0,
                )

    def tick(self, current_tick: int = 0) -> AgentResult:
        """Run one autonomous cycle."""

        incoming = self.process_messages(
            current_tick=current_tick,
        )

        if incoming is not None:
            decision = Decision(
                action=ActionType.SEND_MESSAGE.value,
                reason="Responded to an incoming message.",
                score=0.0,
            )

            self.update_goals(incoming)

            return AgentResult(
                npc_id=self.npc.id,
                decision=decision,
                result=incoming,
            )

        self.observe()

        decision = self.decide()

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

    def process_messages(
        self,
        current_tick: int,
    ) -> ActionResult | None:
        """Process one incoming message."""

        messages = self.social.inbox(
            self.npc.id,
            unprocessed_only=True,
        )

        if not messages:
            return None

        message = messages[0]

        response = self.conversation_engine.respond(
            npc=self.npc,
            message=message,
            social=self.social,
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
