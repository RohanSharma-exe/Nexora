from nexora.social import SocialSystem


def test_message_creates_relationship() -> None:
    social = SocialSystem()

    social.register_npc("alice")
    social.register_npc("bob")

    message = social.send_message(
        sender_id="alice",
        recipient_id="bob",
        content="Hey Bob!",
        tick=1,
    )

    assert message.sender_id == "alice"
    assert message.recipient_id == "bob"
    assert len(social.inbox("bob")) == 1

    relationship = social.get_relationship(
        "alice",
        "bob",
    )

    assert relationship.familiarity > 0
    assert relationship.trust > 0.5


def test_contacts_are_discovered_from_messages() -> None:
    social = SocialSystem()

    social.register_npc("alice")
    social.register_npc("bob")

    social.send_message(
        sender_id="alice",
        recipient_id="bob",
        content="Hello",
        tick=1,
    )

    assert social.contacts("alice") == ["bob"]
    assert social.contacts("bob") == ["alice"]


def test_unknown_recipient_is_rejected() -> None:
    social = SocialSystem()

    social.register_npc("alice")

    try:
        social.send_message(
            sender_id="alice",
            recipient_id="unknown",
            content="Hello",
            tick=1,
        )
    except KeyError:
        return

    raise AssertionError("Expected unknown recipient to raise KeyError")
