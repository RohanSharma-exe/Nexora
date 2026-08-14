from pydantic import BaseModel, Field


class Personality(BaseModel):
    """Stable personality traits for an NPC."""

    ambition: float = Field(default=0.5, ge=0.0, le=1.0)
    curiosity: float = Field(default=0.5, ge=0.0, le=1.0)
    risk_tolerance: float = Field(default=0.5, ge=0.0, le=1.0)
    sociability: float = Field(default=0.5, ge=0.0, le=1.0)
    greed: float = Field(default=0.5, ge=0.0, le=1.0)
    patience: float = Field(default=0.5, ge=0.0, le=1.0)


class Goal(BaseModel):
    """A goal an NPC is trying to accomplish."""

    description: str
    priority: float = Field(default=0.5, ge=0.0, le=1.0)

    target_amount: float | None = Field(
        default=None,
        ge=0.0,
    )

    progress: float = Field(
        default=0.0,
        ge=0.0,
    )

    completed: bool = False

    def add_progress(self, amount: float) -> None:
        """Add progress toward the goal."""

        if amount < 0:
            raise ValueError("Goal progress cannot be negative.")

        self.progress += amount

        if self.target_amount is not None and self.progress >= self.target_amount:
            self.progress = self.target_amount
            self.completed = True


class NPC(BaseModel):
    """The persistent state of an autonomous NPC."""

    id: str
    name: str
    occupation: str

    money: float = Field(default=1000.0, ge=0.0)

    skills: list[str] = Field(default_factory=list)

    personality: Personality = Field(default_factory=Personality)

    goals: list[Goal] = Field(default_factory=list)

    energy: float = Field(default=1.0, ge=0.0, le=1.0)

    reputation: float = Field(default=0.5, ge=0.0, le=1.0)
