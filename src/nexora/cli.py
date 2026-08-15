import typer
from rich.console import Console
from rich.panel import Panel

from nexora.config import load_environment
from nexora.core.world import World
from nexora.models.job import Job, JobDifficulty
from nexora.models.npc import NPC, Goal, Personality
from nexora.reddit.agent import create_discovery_agent
from nexora.reddit.client import RedditRSSClient
from nexora.reddit.models import DiscoveryResult
from nexora.reddit.simulation import build_opportunity_world
from nexora.simulation.engine import SimulationEngine, create_brain

app = typer.Typer(
    name="nexora",
    help="Nexora — an autonomous simulated internet society.",
)

console = Console()


def create_demo_world() -> World:
    """Create the initial demo world."""
    world = World()
    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Python Developer",
        money=1000.0,
        skills=["python", "fastapi", "sql"],
        personality=Personality(
            ambition=0.90,
            curiosity=0.80,
            risk_tolerance=0.90,
            sociability=0.80,
            greed=0.80,
            patience=0.20,
        ),
        goals=[Goal(description="Earn ₹5000", priority=0.90, target_amount=5000.0)],
    )
    bob = NPC(
        id="bob",
        name="Bob",
        occupation="Backend Developer",
        money=1500.0,
        skills=["python", "sql"],
        personality=Personality(
            ambition=0.60,
            curiosity=0.60,
            risk_tolerance=0.30,
            sociability=0.70,
            greed=0.40,
            patience=0.70,
        ),
        goals=[Goal(description="Earn ₹3000", priority=0.80, target_amount=3000.0)],
    )
    sarah = NPC(
        id="sarah",
        name="Sarah",
        occupation="Product Designer",
        money=3000.0,
        skills=["design"],
        personality=Personality(
            ambition=0.70,
            curiosity=0.90,
            risk_tolerance=0.50,
            sociability=0.90,
            greed=0.30,
            patience=0.60,
        ),
        goals=[],
    )
    world.add_npc(alice)
    world.add_npc(bob)
    world.add_npc(sarah)
    world.add_job(
        Job(
            id="job-python-api",
            title="Python API Developer",
            description="Build a small REST API.",
            payment=2500.0,
            required_skills=["python"],
            difficulty=JobDifficulty.MEDIUM,
            employer="Acme Systems",
        )
    )
    world.add_job(
        Job(
            id="job-data-cleaning",
            title="Data Cleaning Task",
            description="Clean and validate a CSV dataset.",
            payment=1500.0,
            required_skills=["python"],
            difficulty=JobDifficulty.EASY,
            employer="DataWorks",
        )
    )
    world.add_job(
        Job(
            id="job-fastapi-fix",
            title="FastAPI Bug Fix",
            description="Fix a production API bug.",
            payment=3500.0,
            required_skills=["fastapi"],
            difficulty=JobDifficulty.HARD,
            employer="CloudForge",
        )
    )
    return world


def _print_opportunities(result: DiscoveryResult) -> None:
    """Print a compact discovery report."""
    for index, opportunity in enumerate(result.opportunities, start=1):
        console.print(
            f"\n[bold cyan]#{index} — {opportunity.problem}[/bold cyan] "
            f"[bold]score={opportunity.score:.0f}/100[/bold]"
        )
        console.print(f"  Customer: {opportunity.target_user}")
        console.print(f"  Solution: {opportunity.solution}")
        console.print(f"  Why now: {opportunity.why_now}")
        for evidence in opportunity.evidence:
            console.print(f"  Evidence: {evidence}")
        for url in opportunity.source_urls:
            console.print(f"  Reddit: {url}")
        for evidence in opportunity.research:
            console.print(f"  Research: {evidence}")


@app.command()
def simulate(
    ticks: int = typer.Option(
        5,
        "--ticks",
        "-t",
        min=1,
        help="Number of simulation ticks.",
    ),
    brain: str | None = typer.Option(
        None,
        "--brain",
        help="Brain: rule, rule-llm, nvidia, gemini, groq, or mistral.",
    ),
) -> None:
    """Run a Nexora simulation."""
    world = create_demo_world()
    selected_brain = None
    if brain is not None:
        try:
            selected_brain = create_brain(brain)
        except ValueError as exc:
            raise typer.BadParameter(str(exc)) from exc

    engine = SimulationEngine(world, brain=selected_brain)
    version_label = (
        "NEXORA V0.6.2 — Rule Brain" if brain == "rule" else "NEXORA V0.6.2 — Legacy Brain"
    )
    console.print(
        Panel.fit(
            f"[bold]{version_label}[/bold]\nAutonomous Internet Society",
            border_style="cyan",
        )
    )
    console.print("\n[bold]NPCs:[/bold]")
    for agent in world.agents.values():
        console.print(f"  • {agent.npc.name} — {agent.npc.occupation}")
    console.print("\n[bold]Available jobs:[/bold]")
    for job in world.job_board.available():
        console.print(f"  • {job.title} — ₹{job.payment:.2f}")

    for tick in range(ticks):
        current_day = world.day
        current_hour = world.hour
        results = engine.tick()
        console.print(f"\n[bold cyan]Tick {tick + 1}[/bold cyan] — Day {current_day}, {current_hour:02d}:00")
        for result in results:
            npc = world.get_npc(result.npc_id)
            console.print(f"\n[bold]{npc.name}[/bold]")
            console.print(f"  Money: ₹{npc.money:.2f}")
            console.print(f"  Reputation: {npc.reputation:.2f}")
            console.print(f"  Decision: {result.decision.action}")
            console.print(f"  Utility: {result.decision.score:.2f}")
            console.print(f"  Reason: {result.decision.reason}")
            console.print(f"  Result: {result.result.message}")
            for goal in npc.goals:
                status = "completed" if goal.completed else "active"
                if goal.target_amount is not None:
                    console.print(
                        f"  Goal: {goal.description} "
                        f"({goal.progress:.0f}/{goal.target_amount:.0f}) [{status}]"
                    )
        console.print("\n[bold magenta]Social activity:[/bold magenta]")
        for message in world.social.history:
            if message.tick == world.tick_count:
                console.print(f"  {message.sender_id} → {message.recipient_id}: {message.content}")
        console.print("\n[bold yellow]Relationships:[/bold yellow]")
        for relationship in world.social.relationships.values():
            console.print(
                f"  {relationship.source_id} → {relationship.target_id} "
                f"trust={relationship.trust:.2f} familiarity={relationship.familiarity:.2f}"
            )


@app.command()
def discover(
    subreddit: str = typer.Option("startups", "--subreddit", "-s"),
    posts: int = typer.Option(8, "--posts", "-p", min=1, max=25),
    research: bool = typer.Option(True, "--research/--no-research"),
) -> None:
    """Watch Reddit, discover pain points, and validate startup opportunities."""
    console.print(
        Panel.fit(
            "[bold]NEXORA — Reddit Opportunity Agent[/bold]\n"
            "Reddit → pain points → opportunities → web validation",
            border_style="green",
        )
    )
    try:
        reddit_posts = RedditRSSClient().hot(subreddit, limit=posts)
        result = create_discovery_agent(research=research).discover(
            subreddit,
            reddit_posts,
            research=research,
        )
    except (RuntimeError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    console.print(f"\n[bold]Observed {len(result.posts)} posts from r/{subreddit}[/bold]")
    _print_opportunities(result)


@app.command("simulate-reddit")
def simulate_reddit(
    subreddit: str = typer.Option("startups", "--subreddit", "-s"),
    posts: int = typer.Option(8, "--posts", "-p", min=1, max=25),
    ticks: int = typer.Option(2, "--ticks", "-t", min=1, max=10),
    brain: str = typer.Option("groq", "--brain"),
    research: bool = typer.Option(True, "--research/--no-research"),
) -> None:
    """Discover Reddit opportunities, then let NPC agents compete over them."""
    try:
        reddit_posts = RedditRSSClient().hot(subreddit, limit=posts)
        discovery = create_discovery_agent(research=research).discover(
            subreddit,
            reddit_posts,
            research=research,
        )
    except (RuntimeError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    _print_opportunities(discovery)
    world = build_opportunity_world(discovery.opportunities)
    try:
        selected_brain = create_brain(brain)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    engine = SimulationEngine(world, brain=selected_brain)
    console.print(
        Panel.fit(
            f"[bold]NEXORA — Reddit Simulation ({brain})[/bold]\n"
            "Discovered opportunities are now simulated as competing jobs.",
            border_style="cyan",
        )
    )
    for tick in range(ticks):
        results = engine.tick()
        console.print(f"\n[bold cyan]Tick {tick + 1}[/bold cyan]")
        for result in results:
            npc = world.get_npc(result.npc_id)
            console.print(
                f"  {npc.name}: {result.decision.action} "
                f"→ {result.decision.target_id or '-'} | {result.decision.reason}"
            )


@app.command()
def version() -> None:
    """Show the Nexora version."""
    console.print("Nexora 0.6.2")


def main() -> None:
    """CLI entry point."""
    load_environment()
    app()


if __name__ == "__main__":
    main()
