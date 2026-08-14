from dataclasses import dataclass, field

from nexora.agent.agent import Agent
from nexora.core.jobs import JobBoard
from nexora.models.job import Job
from nexora.models.npc import NPC


@dataclass
class World:
    """The simulated world containing NPCs and world resources."""

    day: int = 1
    hour: int = 9

    job_board: JobBoard = field(
        default_factory=JobBoard,
    )

    agents: dict[str, Agent] = field(
        default_factory=dict,
    )

    def add_npc(self, npc: NPC) -> None:
        """Add an NPC to the world."""

        if npc.id in self.agents:
            raise ValueError(f"NPC already exists: {npc.id}")

        self.agents[npc.id] = Agent(
            npc=npc,
            job_board=self.job_board,
        )

    def add_job(self, job: Job) -> None:
        """Add a job to the world."""

        self.job_board.add(job)

    def get_npc(self, npc_id: str) -> NPC:
        """Return an NPC by ID."""

        try:
            return self.agents[npc_id].npc
        except KeyError as exc:
            raise KeyError(f"Unknown NPC: {npc_id}") from exc

    def advance_time(self) -> None:
        """Advance the world clock by one hour."""

        self.hour += 1

        if self.hour >= 24:
            self.hour = 0
            self.day += 1
