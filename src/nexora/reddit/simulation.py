"""Build a small simulation world from discovered Reddit opportunities."""

from nexora.core.world import World
from nexora.models.job import Job, JobDifficulty
from nexora.models.npc import Goal, NPC, Personality
from nexora.reddit.models import Opportunity


def build_opportunity_world(opportunities: list[Opportunity]) -> World:
    """Turn discovered opportunities into jobs competing for NPC attention."""
    if not opportunities:
        raise ValueError("At least one opportunity is required.")

    world = World()
    personas = [
        ("maya", "Maya", "Indie Founder", Personality(ambition=0.95, curiosity=0.9, risk_tolerance=0.8, greed=0.7, patience=0.3)),
        ("arjun", "Arjun", "Product Engineer", Personality(ambition=0.7, curiosity=0.95, risk_tolerance=0.5, greed=0.3, patience=0.7)),
        ("neha", "Neha", "B2B Operator", Personality(ambition=0.75, curiosity=0.7, risk_tolerance=0.25, greed=0.5, patience=0.85)),
    ]
    for npc_id, name, occupation, personality in personas:
        world.add_npc(
            NPC(
                id=npc_id,
                name=name,
                occupation=occupation,
                money=1000.0,
                personality=personality,
                goals=[
                    Goal(
                        description="Find the most promising Reddit-backed startup opportunity",
                        priority=0.95,
                    )
                ],
            )
        )

    difficulties = [JobDifficulty.EASY, JobDifficulty.MEDIUM, JobDifficulty.HARD]
    for index, opportunity in enumerate(opportunities[:5]):
        title = opportunity.problem.strip().replace("\n", " ")[:70]
        world.add_job(
            Job(
                id=f"reddit-opportunity-{index + 1}",
                title=title or f"Reddit opportunity {index + 1}",
                description=opportunity.solution,
                payment=max(100.0, opportunity.score * 100.0),
                required_skills=[],
                difficulty=difficulties[min(index, len(difficulties) - 1)],
                employer="Nexora Reddit Discovery",
            )
        )
    return world
