from dataclasses import dataclass, field

from nexora.models.relationship import Relationship


@dataclass(slots=True)
class Message:
    """A message sent between NPCs."""

    sender_id: str
    recipient_id: str
    content: str
    tick: int


@dataclass
class SocialSystem:
    """Manages NPC relationships and messages."""

    relationships: dict[tuple[str, str], Relationship] = field(
        default_factory=dict,
    )

    inboxes: dict[str, list[Message]] = field(
        default_factory=dict,
    )

    history: list[Message] = field(
        default_factory=list,
    )

    def register_npc(self, npc_id: str) -> None:
        """Register an NPC with the social system."""

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

    def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        tick: int,
    ) -> Message:
        """Send a message and update the relationship."""

        if recipient_id not in self.inboxes:
            raise KeyError(f"Unknown recipient: {recipient_id}")

        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            tick=tick,
        )

        self.inboxes[recipient_id].append(message)
        self.history.append(message)

        relationship = self.get_relationship(
            sender_id,
            recipient_id,
        )

        relationship.strengthen()

        return message

    def inbox(self, npc_id: str) -> list[Message]:
        """Return messages received by an NPC."""

        return list(self.inboxes.get(npc_id, []))

    def contacts(self, npc_id: str) -> list[str]:
        """Return NPCs that have interacted with this NPC."""

        contacts: set[str] = set()

        for message in self.history:
            if message.sender_id == npc_id:
                contacts.add(message.recipient_id)

            if message.recipient_id == npc_id:
                contacts.add(message.sender_id)

        return sorted(contacts)

    def unread_count(self, npc_id: str) -> int:
        """Return the number of received messages."""

        return len(self.inboxes.get(npc_id, []))
