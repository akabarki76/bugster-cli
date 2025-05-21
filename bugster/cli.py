"""
Command-line interface for Bugster.
"""

import asyncio
import typer
from rich.console import Console
from typing import Optional

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
    path: Optional[str] = typer.Argument(None, help="Path to test file or directory"),
    headless: Optional[bool] = typer.Option(
        False, "--headless", help="Run tests in headless mode"
    ),
):
    """Run Bugster tests. If no path is provided, runs all tests in .bugster/tests."""
    asyncio.run(test_command(path, headless))


def main():
    app()


if __name__ == "__main__":
    main()
