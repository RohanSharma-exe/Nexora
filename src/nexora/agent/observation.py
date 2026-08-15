"""Build structured observations for NPC brains."""

from nexora.core.jobs import JobBoard
from nexora.memory.memory import MemoryStore
from nexora.models.npc import NPC
from nexora.models.runtime import Observation
from nexora.social import SocialSystem


class ObservationBuilder:
    """Construct the information visible to an NPC brain."""

    def __init__(
        self,
        job_board: JobBoard,
        social: SocialSystem,
        memory: MemoryStore,
    ) -> None:
        self.job_board = job_board
        self.social = social
        self.memory = memory

    def build(
        self,
        npc: NPC,
        tick: int,
    ) -> Observation:
        """Build an immutable observation from the current world state."""

        goals = tuple(goal.description for goal in npc.goals if not goal.completed)

        events = tuple(
            self._format_message(message.sender_id, message.content)
            for message in self.social.inbox(
                npc.id,
                unprocessed_only=True,
            )
        )

        memories = tuple(memory.content for memory in self.memory.recent(limit=5))

        contacts = tuple(self.social.ranked_contacts(npc.id))

        available_actions = self._available_actions(
            npc=npc,
            has_events=bool(events),
            has_jobs=self._has_suitable_jobs(npc),
            has_contacts=bool(contacts),
        )

        return Observation(
            subject_id=npc.id,
            tick=tick,
            events=events,
            memories=memories,
            goals=goals,
            contacts=contacts,
            available_actions=available_actions,
        )

    def _has_suitable_jobs(self, npc: NPC) -> bool:
        """Return whether a suitable open job exists."""

        return any(job.is_suitable_for(npc.skills) for job in self.job_board.available())

    def _available_actions(
        self,
        npc: NPC,
        has_events: bool,
        has_jobs: bool,
        has_contacts: bool,
    ) -> tuple[str, ...]:
        """Determine which high-level actions are currently possible."""

        actions: list[str] = [
            "idle",
            "wait",
        ]

        has_active_goal = any(not goal.completed for goal in npc.goals)

        if has_active_goal and has_jobs:
            actions.append("complete_job")

        if has_events and has_contacts:
            actions.append("send_message")

        if not has_active_goal and has_contacts:
            actions.append("send_message")

        return tuple(actions)

    @staticmethod
    def _format_message(
        sender_id: str,
        content: str,
    ) -> str:
        """Convert an incoming message into an observation event."""

        return f"{sender_id}: {content}"
