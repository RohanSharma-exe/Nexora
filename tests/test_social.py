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


def test_higher_trust_contact_is_preferred() -> None:
    social = SocialSystem()

    social.register_npc("alice")
    social.register_npc("bob")
    social.register_npc("sarah")

    social.send_message(
        sender_id="alice",
        recipient_id="bob",
        content="Hello Bob",
        tick=1,
    )

    social.send_message(
        sender_id="alice",
        recipient_id="sarah",
        content="Hello Sarah",
        tick=1,
    )

    bob = social.get_relationship(
        "alice",
        "bob",
    )

    bob.trust = 0.9
    bob.respect = 0.9
    bob.familiarity = 0.8

    sarah = social.get_relationship(
        "alice",
        "sarah",
    )

    sarah.trust = 0.2
    sarah.respect = 0.2
    sarah.familiarity = 0.2

    assert social.suggest_contact("alice") == "bob"


def test_ranked_contacts_follow_relationship_strength() -> None:
    social = SocialSystem()

    for npc_id in ("alice", "bob", "sarah", "john"):
        social.register_npc(npc_id)

    for target in ("bob", "sarah", "john"):
        social.send_message(
            sender_id="alice",
            recipient_id=target,
            content="Hello",
            tick=1,
        )

    social.get_relationship(
        "alice",
        "bob",
    ).trust = 0.6

    social.get_relationship(
        "alice",
        "sarah",
    ).trust = 0.9

    social.get_relationship(
        "alice",
        "john",
    ).trust = 0.3

    assert social.ranked_contacts("alice") == [
        "sarah",
        "bob",
        "john",
    ]


def test_relationship_outcome_can_increase_trust() -> None:
    social = SocialSystem()

    social.register_npc("alice")
    social.register_npc("bob")

    relationship = social.get_relationship(
        "alice",
        "bob",
    )

    original_trust = relationship.trust

    social.apply_relationship_outcome(
        source_id="alice",
        target_id="bob",
        trust_delta=0.15,
        respect_delta=0.10,
    )

    assert relationship.trust == original_trust + 0.15
    assert relationship.respect == 0.60


def test_relationship_outcome_can_decrease_trust() -> None:
    social = SocialSystem()

    social.register_npc("alice")
    social.register_npc("bob")

    relationship = social.get_relationship(
        "alice",
        "bob",
    )

    social.apply_relationship_outcome(
        source_id="alice",
        target_id="bob",
        trust_delta=-0.20,
    )

    assert relationship.trust == 0.30


def test_relationship_values_are_clamped() -> None:
    social = SocialSystem()

    social.register_npc("alice")
    social.register_npc("bob")

    relationship = social.get_relationship(
        "alice",
        "bob",
    )

    social.apply_relationship_outcome(
        source_id="alice",
        target_id="bob",
        trust_delta=10.0,
        respect_delta=10.0,
        familiarity_delta=10.0,
    )

    assert relationship.trust == 1.0
    assert relationship.respect == 1.0
    assert relationship.familiarity == 1.0

    social.apply_relationship_outcome(
        source_id="alice",
        target_id="bob",
        trust_delta=-10.0,
        respect_delta=-10.0,
        familiarity_delta=-10.0,
    )

    assert relationship.trust == 0.0
    assert relationship.respect == 0.0
    assert relationship.familiarity == 0.0
