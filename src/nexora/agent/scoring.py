from dataclasses import dataclass

from nexora.models.job import Job, JobDifficulty
from nexora.models.npc import NPC

_DIFFICULTY_RISK = {
    JobDifficulty.EASY: 0.2,
    JobDifficulty.MEDIUM: 0.5,
    JobDifficulty.HARD: 0.9,
}


@dataclass(frozen=True, slots=True)
class JobScore:
    """Utility score for an NPC evaluating a job."""

    job_id: str
    score: float
    payment_score: float
    risk_penalty: float
    personality_bonus: float


class UtilityScorer:
    """Scores opportunities according to NPC personality."""

    def score_job(
        self,
        npc: NPC,
        job: Job,
        maximum_payment: float,
    ) -> JobScore:
        if maximum_payment <= 0:
            raise ValueError("Maximum payment must be positive.")

        payment_score = job.payment / maximum_payment

        difficulty_risk = _DIFFICULTY_RISK[job.difficulty]

        risk_penalty = difficulty_risk * (1.0 - npc.personality.risk_tolerance)

        payment_utility = payment_score * (
            0.45 + 0.25 * npc.personality.greed + 0.15 * npc.personality.ambition
        )

        risk_utility = (1.0 - risk_penalty) * 0.20

        personality_bonus = npc.personality.ambition * difficulty_risk * 0.10

        score = payment_utility + 0.15 + risk_utility + personality_bonus

        return JobScore(
            job_id=job.id,
            score=score,
            payment_score=payment_score,
            risk_penalty=risk_penalty,
            personality_bonus=personality_bonus,
        )

    def score_wait(self, npc: NPC) -> float:
        """Score waiting for a potentially better opportunity."""

        return (
            npc.personality.patience * 0.55
            + (1.0 - npc.personality.risk_tolerance) * 0.25
            + (1.0 - npc.personality.ambition) * 0.10
        )
