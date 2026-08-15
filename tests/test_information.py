from nexora.agent.information import InformationSharingEngine
from nexora.models.information import Information, InformationType
from nexora.models.npc import NPC, Personality
from nexora.models.relationship import Relationship


def create_information() -> Information:
    return Information(
        id="job-1",
        type=InformationType.JOB,
        title="FastAPI Bug Fix",
        content="FastAPI bug fix paying ₹3500.",
        source_id="system",
        value=0.8,
    )


def create_relationship(
    trust: float = 0.5,
    familiarity: float = 0.5,
) -> Relationship:
    return Relationship(
        source_id="alice",
        target_id="bob",
        trust=trust,
        familiarity=familiarity,
    )


def test_high_trust_npc_shares_valuable_information() -> None:
    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        personality=Personality(
            ambition=0.5,
            curiosity=0.8,
            risk_tolerance=0.5,
            sociability=0.8,
            greed=0.1,
            patience=0.5,
        ),
        reputation=0.9,
    )

    recipient = NPC(
        id="bob",
        name="Bob",
        occupation="Developer",
    )

    decision = InformationSharingEngine().decide(
        npc=npc,
        recipient=recipient,
        relationship=create_relationship(
            trust=0.9,
            familiarity=0.8,
        ),
        information=create_information(),
    )

    assert decision.should_share
    assert decision.score >= 0.50


def test_low_trust_greedy_npc_keeps_information() -> None:
    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        personality=Personality(
            ambition=0.9,
            curiosity=0.1,
            risk_tolerance=0.5,
            sociability=0.1,
            greed=0.9,
            patience=0.5,
        ),
        reputation=0.1,
    )

    recipient = NPC(
        id="bob",
        name="Bob",
        occupation="Developer",
    )

    decision = InformationSharingEngine().decide(
        npc=npc,
        recipient=recipient,
        relationship=create_relationship(
            trust=0.1,
            familiarity=0.05,
        ),
        information=create_information(),
    )

    assert not decision.should_share
    assert decision.score < 0.50


def test_information_value_increases_sharing_probability() -> None:
    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        personality=Personality(
            ambition=0.5,
            curiosity=0.7,
            risk_tolerance=0.5,
            sociability=0.7,
            greed=0.3,
            patience=0.5,
        ),
        reputation=0.7,
    )

    recipient = NPC(
        id="bob",
        name="Bob",
        occupation="Developer",
    )

    relationship = create_relationship(
        trust=0.5,
        familiarity=0.5,
    )

    low_value = Information(
        id="low",
        type=InformationType.JOB,
        title="Small Task",
        content="Small task.",
        source_id="system",
        value=0.1,
    )

    high_value = Information(
        id="high",
        type=InformationType.JOB,
        title="High Paying Job",
        content="High paying job.",
        source_id="system",
        value=1.0,
    )

    engine = InformationSharingEngine()

    low_decision = engine.decide(
        npc=npc,
        recipient=recipient,
        relationship=relationship,
        information=low_value,
    )

    high_decision = engine.decide(
        npc=npc,
        recipient=recipient,
        relationship=relationship,
        information=high_value,
    )

    assert high_decision.score > low_decision.score


def test_information_expiration() -> None:
    information = Information(
        id="job-1",
        type=InformationType.JOB,
        title="Temporary Job",
        content="Temporary opportunity.",
        source_id="system",
        expires_at_tick=10,
    )

    assert not information.is_expired(9)
    assert information.is_expired(10)
    assert information.is_expired(20)


def test_information_without_expiration_never_expires() -> None:
    information = Information(
        id="person-1",
        type=InformationType.PERSON,
        title="Alice",
        content="Alice is a Python developer.",
        source_id="system",
    )

    assert not information.is_expired(1)
    assert not information.is_expired(1000)
