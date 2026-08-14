from pydantic import BaseModel, Field


class Relationship(BaseModel):
    """Relationship between two NPCs."""

    source_id: str
    target_id: str

    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    respect: float = Field(default=0.5, ge=0.0, le=1.0)
    familiarity: float = Field(default=0.0, ge=0.0, le=1.0)

    def strengthen(self, amount: float = 0.05) -> None:
        """Increase familiarity and trust."""

        self.familiarity = min(
            1.0,
            self.familiarity + amount,
        )

        self.trust = min(
            1.0,
            self.trust + amount * 0.5,
        )

    def weaken(self, amount: float = 0.05) -> None:
        """Decrease trust."""

        self.trust = max(
            0.0,
            self.trust - amount,
        )

    def adjust_trust(self, amount: float) -> None:
        """Adjust trust while keeping it within bounds."""

        self.trust = min(
            1.0,
            max(0.0, self.trust + amount),
        )

    def adjust_respect(self, amount: float) -> None:
        """Adjust respect while keeping it within bounds."""

        self.respect = min(
            1.0,
            max(0.0, self.respect + amount),
        )

    def adjust_familiarity(self, amount: float) -> None:
        """Adjust familiarity while keeping it within bounds."""

        self.familiarity = min(
            1.0,
            max(0.0, self.familiarity + amount),
        )
