import pytest

from nexora.core.jobs import JobBoard
from nexora.models.job import Job
from nexora.models.npc import NPC


def test_job_requires_matching_skill() -> None:
    job = Job(
        id="job-1",
        title="Python Developer",
        description="Build an API.",
        payment=2000,
        required_skills=["python"],
    )

    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Designer",
        skills=["design"],
    )

    assert job.is_suitable_for(npc.skills) is False


def test_job_accepts_matching_skill() -> None:
    job = Job(
        id="job-1",
        title="Python Developer",
        description="Build an API.",
        payment=2000,
        required_skills=["python"],
    )

    npc = NPC(
        id="alice",
        name="Alice",
        occupation="Developer",
        skills=["python"],
    )

    assert job.is_suitable_for(npc.skills) is True


def test_job_board_rejects_duplicate_jobs() -> None:
    job = Job(
        id="job-1",
        title="Python Developer",
        description="Build an API.",
        payment=2000,
    )

    board = JobBoard()
    board.add(job)

    with pytest.raises(ValueError):
        board.add(job)


def test_completed_job_is_removed_from_available_jobs() -> None:
    job = Job(
        id="job-1",
        title="Python Developer",
        description="Build an API.",
        payment=2000,
    )

    board = JobBoard([job])

    board.complete("job-1")

    assert board.available() == []
