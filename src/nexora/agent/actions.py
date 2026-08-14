from dataclasses import dataclass
from enum import StrEnum

from nexora.core.jobs import JobBoard
from nexora.memory.memory import MemoryStore
from nexora.models.npc import NPC


class ActionType(StrEnum):
    """Actions currently available to an NPC."""

    LOOK_FOR_WORK = "look_for_work"
    COMPLETE_JOB = "complete_job"
    REST = "rest"
    IDLE = "idle"


@dataclass(slots=True)
class Action:
    """An action selected by an NPC."""

    type: ActionType
    target_id: str | None = None
    reason: str = ""


@dataclass(slots=True)
class ActionResult:
    """Result produced after executing an action."""

    success: bool
    message: str
    money_change: float = 0.0


class ActionExecutor:
    """Executes actions against the simulated world."""

    def __init__(
        self,
        job_board: JobBoard,
        memory: MemoryStore,
    ) -> None:
        self.job_board = job_board
        self.memory = memory

    def execute(
        self,
        npc: NPC,
        action: Action,
    ) -> ActionResult:
        """Execute an action and mutate NPC/world state."""

        if action.type == ActionType.LOOK_FOR_WORK:
            return self._look_for_work(npc)

        if action.type == ActionType.COMPLETE_JOB:
            return self._complete_job(npc, action)

        if action.type == ActionType.REST:
            return self._rest(npc)

        return ActionResult(
            success=True,
            message=f"{npc.name} is idle.",
        )

    def _look_for_work(self, npc: NPC) -> ActionResult:
        jobs = [job for job in self.job_board.available() if job.is_suitable_for(npc.skills)]

        if not jobs:
            message = f"{npc.name} found no suitable jobs."

            self.memory.add(
                content=message,
                importance=0.4,
            )

            return ActionResult(
                success=False,
                message=message,
            )

        best_job = max(
            jobs,
            key=lambda job: job.payment,
        )

        message = f"{npc.name} found a suitable job: {best_job.title} for ₹{best_job.payment:.2f}."

        self.memory.add(
            content=message,
            importance=0.6,
        )

        return ActionResult(
            success=True,
            message=message,
        )

    def _complete_job(
        self,
        npc: NPC,
        action: Action,
    ) -> ActionResult:
        if action.target_id is None:
            return ActionResult(
                success=False,
                message="No job was specified.",
            )

        try:
            job = self.job_board.get(action.target_id)
        except KeyError:
            return ActionResult(
                success=False,
                message=f"Unknown job: {action.target_id}",
            )

        if not job.is_suitable_for(npc.skills):
            return ActionResult(
                success=False,
                message=(f"{npc.name} does not have the skills required for {job.title}."),
            )

        if job.status.value != "open":
            return ActionResult(
                success=False,
                message=f"{job.title} is no longer available.",
            )

        self.job_board.complete(job.id)

        npc.money += job.payment

        message = f"{npc.name} completed '{job.title}' and earned ₹{job.payment:.2f}."

        self.memory.add(
            content=message,
            importance=0.9,
        )

        return ActionResult(
            success=True,
            message=message,
            money_change=job.payment,
        )

    def _rest(self, npc: NPC) -> ActionResult:
        previous_energy = npc.energy

        npc.energy = min(
            1.0,
            npc.energy + 0.25,
        )

        recovered = npc.energy - previous_energy

        message = f"{npc.name} rested and recovered {recovered:.2f} energy."

        self.memory.add(
            content=message,
            importance=0.2,
        )

        return ActionResult(
            success=True,
            message=message,
        )
