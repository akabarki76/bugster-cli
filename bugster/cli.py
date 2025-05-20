"""
Command-line interface for Bugster.
"""

import typer
from rich.console import Console

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
def test():
    """Run Bugster CLI configuration."""
    test_command()


@app.command()
def analyze(
    show_logs: bool = typer.Option(
        False,
        "--show-logs",
        help="Show detailed logs during analysis",
    ),
):
    """Run Bugster CLI analysis command."""
    analyze_command(options={"show_logs": show_logs})


def main():
    app()


if __name__ == "__main__":
    main()
