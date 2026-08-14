from dataclasses import dataclass, field

from nexora.core.jobs import JobBoard
from nexora.models.conversation import (
    ConversationMemory,
    ConversationMessage,
    MessageIntent,
)
from nexora.models.relationship import Relationship


@dataclass
class SocialSystem:
    """Manages relationships, conversations, and social memory."""

    job_board: JobBoard | None = None

    relationships: dict[tuple[str, str], Relationship] = field(
        default_factory=dict,
    )

    inboxes: dict[str, list[ConversationMessage]] = field(
        default_factory=dict,
    )

    history: list[ConversationMessage] = field(
        default_factory=list,
    )

    memories: list[ConversationMemory] = field(
        default_factory=list,
    )

    last_message_tick: dict[tuple[str, str], int] = field(
        default_factory=dict,
    )

    _next_message_id: int = 1

    def register_npc(self, npc_id: str) -> None:
        """Register an NPC."""

        if npc_id not in self.inboxes:
            self.inboxes[npc_id] = []

    def get_relationship(
        self,
        source_id: str,
        target_id: str,
    ) -> Relationship:
        """Return or create a relationship."""

        key = (source_id, target_id)

        if key not in self.relationships:
            self.relationships[key] = Relationship(
                source_id=source_id,
                target_id=target_id,
            )

        return self.relationships[key]

    def relationship_score(
        self,
        source_id: str,
        target_id: str,
    ) -> float:
        """Calculate how attractive a relationship is to an NPC."""

        relationship = self.get_relationship(
            source_id,
            target_id,
        )

        return (
            relationship.trust * 0.5 + relationship.respect * 0.3 + relationship.familiarity * 0.2
        )

    def apply_relationship_outcome(
        self,
        source_id: str,
        target_id: str,
        trust_delta: float = 0.0,
        respect_delta: float = 0.0,
        familiarity_delta: float = 0.0,
    ) -> Relationship:
        """Apply the consequences of an interaction."""

        relationship = self.get_relationship(
            source_id,
            target_id,
        )

        relationship.adjust_trust(trust_delta)
        relationship.adjust_respect(respect_delta)
        relationship.adjust_familiarity(familiarity_delta)

        return relationship

    def can_message(
        self,
        sender_id: str,
        recipient_id: str,
        tick: int,
        cooldown: int = 2,
    ) -> bool:
        """Return whether a sender can message a recipient."""

        last_tick = self.last_message_tick.get((sender_id, recipient_id))

        if last_tick is None:
            return True

        return tick - last_tick >= cooldown

    def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        tick: int,
        intent: MessageIntent = MessageIntent.CASUAL,
    ) -> ConversationMessage:
        """Send and persist a message."""

        if sender_id not in self.inboxes:
            raise KeyError(f"Unknown sender: {sender_id}")

        if recipient_id not in self.inboxes:
            raise KeyError(f"Unknown recipient: {recipient_id}")

        if not self.can_message(
            sender_id,
            recipient_id,
            tick,
        ):
            raise ValueError(f"Message cooldown active: {sender_id} -> {recipient_id}")

        message = ConversationMessage(
            id=self._next_message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            intent=intent,
            tick=tick,
        )

        self._next_message_id += 1

        self.inboxes[recipient_id].append(message)
        self.history.append(message)

        self.last_message_tick[(sender_id, recipient_id)] = tick

        relationship = self.get_relationship(
            sender_id,
            recipient_id,
        )

        relationship.strengthen()

        return message

    def inbox(
        self,
        npc_id: str,
        unprocessed_only: bool = False,
    ) -> list[ConversationMessage]:
        """Return an NPC's inbox."""

        messages = self.inboxes.get(npc_id, [])

        if unprocessed_only:
            return [message for message in messages if not message.processed]

        return list(messages)

    def process_message(
        self,
        npc_id: str,
        message_id: int,
    ) -> ConversationMessage:
        """Mark a message as processed."""

        for message in self.inboxes.get(npc_id, []):
            if message.id == message_id:
                message.processed = True
                return message

        raise KeyError(f"Message {message_id} not found for {npc_id}")

    def remember(
        self,
        message: ConversationMessage,
        npc_id: str,
        summary: str,
        importance: float = 0.5,
    ) -> ConversationMemory:
        """Store a conversational memory."""

        memory = ConversationMemory(
            message_id=message.id,
            npc_id=npc_id,
            other_npc_id=message.sender_id,
            summary=summary,
            importance=importance,
        )

        self.memories.append(memory)

        return memory

    def memories_for(
        self,
        npc_id: str,
        other_npc_id: str | None = None,
    ) -> list[ConversationMemory]:
        """Retrieve conversational memories."""

        memories = [memory for memory in self.memories if memory.npc_id == npc_id]

        if other_npc_id is not None:
            memories = [memory for memory in memories if memory.other_npc_id == other_npc_id]

        return memories

    def contacts(
        self,
        npc_id: str,
    ) -> list[str]:
        """Return NPCs that have interacted with this NPC."""

        contacts: set[str] = set()

        for message in self.history:
            if message.sender_id == npc_id:
                contacts.add(message.recipient_id)

            if message.recipient_id == npc_id:
                contacts.add(message.sender_id)

        return sorted(contacts)

    def ranked_contacts(
        self,
        npc_id: str,
    ) -> list[str]:
        """Return contacts ordered by relationship strength."""

        contacts = self.contacts(npc_id)

        return sorted(
            contacts,
            key=lambda contact: (
                -self.relationship_score(
                    npc_id,
                    contact,
                ),
                contact,
            ),
        )

    def unread_count(
        self,
        npc_id: str,
    ) -> int:
        """Return the number of unprocessed messages."""

        return len(
            self.inbox(
                npc_id,
                unprocessed_only=True,
            )
        )

    def suggest_contact(
        self,
        npc_id: str,
    ) -> str | None:
        """Suggest the strongest available social connection."""

        candidates = sorted(candidate for candidate in self.inboxes if candidate != npc_id)

        if not candidates:
            return None

        ranked = sorted(
            candidates,
            key=lambda candidate: (
                -self.relationship_score(
                    npc_id,
                    candidate,
                ),
                candidate,
            ),
        )

        return ranked[0]
