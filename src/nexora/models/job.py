from enum import StrEnum

from pydantic import BaseModel, Field


class JobDifficulty(StrEnum):
    """Difficulty levels for simulated jobs."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class JobStatus(StrEnum):
    """Lifecycle state of a job."""

    OPEN = "open"
    COMPLETED = "completed"


class Job(BaseModel):
    """A job available in the simulated economy."""

    id: str
    title: str
    description: str

    payment: float = Field(gt=0)

    required_skills: list[str] = Field(default_factory=list)

    difficulty: JobDifficulty = JobDifficulty.MEDIUM

    status: JobStatus = JobStatus.OPEN

    employer: str = "system"

    def is_suitable_for(self, skills: list[str]) -> bool:
        """Return whether the NPC has all required skills."""

        available_skills = {skill.lower() for skill in skills}

        return all(
            required_skill.lower() in available_skills for required_skill in self.required_skills
        )
