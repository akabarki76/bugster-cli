"""
Command-line interface for Bugster.
"""

import asyncio
import typer
from rich.console import Console
from typing import Optional


app = typer.Typer()
console = Console()


@app.command()
def init():
    """Initialize Bugster CLI configuration."""
    from bugster.commands.init import init_command

    init_command()


@app.command()
def login():
    """Login to Bugster by setting up your API key."""
    from bugster.commands.login import login_command

    login_command()


@app.command()
def test(
    path: Optional[str] = typer.Argument(None, help="Path to test file or directory"),
    headless: Optional[bool] = typer.Option(
        False, "--headless", help="Run tests in headless mode"
    ),
    silent: Optional[bool] = typer.Option(
        False, "--silent", "-s", help="Run in silent mode (less verbose output)"
    ),
):
    """Run Bugster tests. If no path is provided, runs all tests in .bugster/tests."""
    from bugster.commands.test import test_command

    asyncio.run(test_command(path, headless, silent))


@app.command()
def analyze(
    show_logs: bool = typer.Option(
        False,
        "--show-logs",
        help="Show detailed logs during analysis",
    ),
    force: bool = typer.Option(
        False,
        "-f",
        "--force",
        help="Force analysis even if the codebase has already been analyzed",
    ),
):
    """Run Bugster CLI analysis command."""
    from bugster.commands.analyze import analyze_command

    analyze_command(options={"show_logs": show_logs, "force": force})


def main():
    app()


if __name__ == "__main__":
    main()
