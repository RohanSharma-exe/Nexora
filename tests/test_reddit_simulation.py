from nexora.reddit.models import Opportunity
from nexora.reddit.simulation import build_opportunity_world


def test_opportunities_become_simulation_jobs() -> None:
    opportunity = Opportunity(
        problem="Manual reporting",
        target_user="small teams",
        solution="AI reporting assistant",
        why_now="Teams are overloaded",
        evidence=["Repeated complaints"],
        source_urls=["https://www.reddit.com/r/startups/comments/test/"],
        score=84,
    )

    world = build_opportunity_world([opportunity])

    assert len(world.agents) == 3
    jobs = world.job_board.available()
    assert len(jobs) == 1
    assert jobs[0].payment == 8400.0
