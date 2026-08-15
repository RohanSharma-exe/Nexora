from nexora.models.npc import NPC
from nexora.social import SocialSystem


def test_reputation_can_increase() -> None:
    social = SocialSystem()

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    social.register_npc(alice)

    social.adjust_reputation(
        npc_id="alice",
        delta=0.2,
    )

    assert alice.reputation == 0.7


def test_reputation_can_decrease() -> None:
    social = SocialSystem()

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    social.register_npc(alice)

    social.adjust_reputation(
        npc_id="alice",
        delta=-0.2,
    )

    assert alice.reputation == 0.3


def test_reputation_is_clamped() -> None:
    social = SocialSystem()

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    social.register_npc(alice)

    social.adjust_reputation(
        npc_id="alice",
        delta=10.0,
    )

    assert alice.reputation == 1.0

    social.adjust_reputation(
        npc_id="alice",
        delta=-10.0,
    )

    assert alice.reputation == 0.0


def test_unknown_npc_reputation_raises() -> None:
    social = SocialSystem()

    try:
        social.adjust_reputation(
            npc_id="unknown",
            delta=0.1,
        )
    except KeyError:
        return

    raise AssertionError("Expected KeyError for unknown NPC")


def test_reputation_score_returns_registered_value() -> None:
    social = SocialSystem()

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        reputation=0.8,
    )

    social.register_npc(alice)

    assert social.reputation_score("alice") == 0.8


def test_reputation_score_defaults_for_unknown_npc() -> None:
    social = SocialSystem()

    assert social.reputation_score("unknown") == 0.5


def test_reputation_is_clamped_to_one() -> None:
    social = SocialSystem()

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    social.register_npc(alice)

    social.adjust_reputation(
        npc_id="alice",
        delta=10.0,
    )

    assert alice.reputation == 1.0


def test_reputation_is_clamped_to_zero() -> None:
    social = SocialSystem()

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    social.register_npc(alice)

    social.adjust_reputation(
        npc_id="alice",
        delta=-10.0,
    )

    assert alice.reputation == 0.0
