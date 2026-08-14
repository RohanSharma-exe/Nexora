import typer
from rich.console import Console
from rich.panel import Panel

from nexora.core.world import World
from nexora.models.job import Job, JobDifficulty
from nexora.models.npc import NPC, Goal, Personality
from nexora.simulation.engine import SimulationEngine

app = typer.Typer(
    name="nexora",
    help="Nexora — an autonomous simulated internet society.",
)

console = Console()


def create_demo_world() -> World:
    """Create the initial V0.1 world."""

    world = World()

    alice = NPC(
        id="alice",
        name="Alice",
        occupation="Python Developer",
        money=1000.0,
        skills=[
            "python",
            "fastapi",
            "sql",
        ],
        personality=Personality(
            ambition=0.85,
            curiosity=0.80,
            risk_tolerance=0.55,
            sociability=0.60,
            greed=0.40,
            patience=0.65,
        ),
        goals=[
            Goal(
                description="Earn ₹5000",
                priority=0.90,
                target_amount=5000.0,
            ),
        ],
    )

    world.add_npc(alice)

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


@app.command()
def simulate(
    ticks: int = typer.Option(
        5,
        "--ticks",
        "-t",
        min=1,
        help="Number of simulation ticks.",
    ),
) -> None:
    """Run a Nexora simulation."""

    world = create_demo_world()
    engine = SimulationEngine(world)

    console.print(
        Panel.fit(
            "[bold]NEXORA V0.1.1[/bold]\nCorrected Agent Loop",
            border_style="cyan",
        )
    )

    console.print("\n[bold]Available jobs:[/bold]")

    for job in world.job_board.available():
        console.print(f"  • {job.title} — ₹{job.payment:.2f}")

    for tick in range(ticks):
        current_day = world.day
        current_hour = world.hour

        results = engine.tick()

        console.print(
            f"\n[bold cyan]Tick {tick + 1}[/bold cyan] — Day {current_day}, {current_hour:02d}:00"
        )

        for result in results:
            npc = world.get_npc(result.npc_id)

            console.print(f"\n[bold]{npc.name}[/bold]")
            console.print(f"  Money: ₹{npc.money:.2f}")
            console.print(f"  Decision: {result.decision.action}")
            console.print(f"  Reason: {result.decision.reason}")
            console.print(f"  Result: {result.result.message}")

            for goal in npc.goals:
                status = "completed" if goal.completed else "active"

                if goal.target_amount is not None:
                    console.print(
                        f"  Goal: {goal.description} "
                        f"({goal.progress:.0f}/"
                        f"{goal.target_amount:.0f}) "
                        f"[{status}]"
                    )
                else:
                    console.print(f"  Goal: {goal.description} [{status}]")


@app.command()
def version() -> None:
    """Show the Nexora version."""

    console.print("Nexora 0.1.1")


def main() -> None:
    """CLI entry point."""

    app()


if __name__ == "__main__":
    main()
