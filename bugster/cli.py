"""
Command-line interface for Bugster.
"""

import asyncio
import typer
from rich.console import Console
from typing import Optional

from bugster.commands.analyze import analyze_command
from bugster.commands.init import init_command
from bugster.commands.test import test_command

app = typer.Typer()
console = Console()


@app.command()
def init():
    """Initialize Bugster CLI configuration."""
    init_command()


@app.command()
def test(
    path: Optional[str] = typer.Argument(None, help="Path to test file or directory")
):
    """Run Bugster tests. If no path is provided, runs all tests in .bugster/tests."""
    asyncio.run(test_command(path))


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
    analyze_command(options={"show_logs": show_logs, "force": force})


def main():
    app()


if __name__ == "__main__":
    main()
