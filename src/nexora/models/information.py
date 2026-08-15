from dataclasses import dataclass
from enum import StrEnum


class InformationType(StrEnum):
    JOB = "job"
    PERSON = "person"
    RESOURCE = "resource"
    OPPORTUNITY = "opportunity"
    WARNING = "warning"


@dataclass(frozen=True)
class Information:
    id: str
    type: InformationType
    title: str
    content: str
    source_id: str
    value: float = 0.5
    expires_at_tick: int | None = None

    def is_expired(self, current_tick: int) -> bool:
        if self.expires_at_tick is None:
            return False

        return current_tick >= self.expires_at_tick
