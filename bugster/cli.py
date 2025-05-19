"""
Command-line interface for Bugster.
"""

import typer
from rich.console import Console

from bugster.commands.init import init_command
from bugster.commands.test import test_command

app = typer.Typer()
console = Console()


@app.command()
def init():
    """Initialize Bugster CLI configuration."""
    init_command()


@app.command()
def test():
    """Run Bugster CLI configuration."""
    test_command()


def main():
    app()


if __name__ == "__main__":
    main()
