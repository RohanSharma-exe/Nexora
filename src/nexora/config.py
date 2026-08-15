"""Application configuration helpers."""

from pathlib import Path

from dotenv import load_dotenv


def load_environment() -> None:
    """Load local environment variables from the project's .env file."""
    env_file = Path.cwd() / ".env"
    load_dotenv(dotenv_path=env_file, override=False)
