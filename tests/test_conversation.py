from nexora.agent.conversation import ConversationEngine
from nexora.core.jobs import JobBoard
from nexora.models.conversation import (
    ConversationMessage,
    MessageIntent,
)
from nexora.models.job import Job
from nexora.models.npc import NPC
from nexora.social import SocialSystem


def test_question_about_work_gets_contextual_response() -> None:
    jobs = JobBoard(
        [
            Job(
                id="job-1",
                title="Python API Job",
                description="Build an API.",
                payment=3000,
                required_skills=["python"],
            )
        ]
    )

    social = SocialSystem(
        job_board=jobs,
    )

    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        skills=["python"],
    )

    message = ConversationMessage(
        id=1,
        sender_id="bob",
        recipient_id="alice",
        content="Do you know of any work?",
        intent=MessageIntent.QUESTION,
        tick=1,
    )

    response = ConversationEngine().respond(
        npc=npc,
        message=message,
        job_board=jobs,
    )

    assert "Python API Job" in response.content
    assert "3000" in response.content
    assert response.intent == MessageIntent.OFFER


def test_thanks_gets_polite_response() -> None:
    social = SocialSystem()

    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
    )

    message = ConversationMessage(
        id=1,
        sender_id="bob",
        recipient_id="alice",
        content="Thanks for your help!",
        intent=MessageIntent.THANKS,
        tick=1,
    )

    response = ConversationEngine().respond(
        npc=npc,
        message=message,
        job_board=JobBoard(),
    )

    assert response.content == "You're welcome!"


def test_processed_message_is_not_unread() -> None:
    social = SocialSystem()

    social.register_npc("alice")
    social.register_npc("bob")

    message = social.send_message(
        sender_id="bob",
        recipient_id="alice",
        content="Hello!",
        tick=1,
        intent=MessageIntent.GREETING,
    )

    assert social.unread_count("alice") == 1

    social.process_message(
        npc_id="alice",
        message_id=message.id,
    )

    assert social.unread_count("alice") == 0


def test_conversation_memory_is_persistent() -> None:
    social = SocialSystem()

    social.register_npc("alice")
    social.register_npc("bob")

    message = social.send_message(
        sender_id="bob",
        recipient_id="alice",
        content="I found a new job.",
        tick=1,
        intent=MessageIntent.OFFER,
    )

    memory = social.remember(
        message=message,
        npc_id="alice",
        summary="Bob found a new job.",
        importance=0.8,
    )

    memories = social.memories_for("alice")

    assert memory in memories
    assert memories[0].summary == "Bob found a new job."
