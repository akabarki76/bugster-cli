"""Command-line interface for Bugster."""

import asyncio
import sys
from typing import Optional

import click
import typer
from rich.console import Console
from loguru import logger

from bugster import __version__
from bugster.utils.colors import BugsterColors

app = typer.Typer(
    name="bugster",
    add_completion=False,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


def version_callback(value: bool):
    if value:
        # Create a styled version output
        console = Console()
        console.print()
        console.print(f"🐛 [bold {BugsterColors.PRIMARY}]Bugster CLI[/bold {BugsterColors.PRIMARY}]", justify="center")
        console.print(f"[{BugsterColors.TEXT_DIM}]Version[/{BugsterColors.TEXT_DIM}] [bold {BugsterColors.SUCCESS}]{__version__}[/bold {BugsterColors.SUCCESS}]", justify="center")
        console.print()
        console.print(f"[{BugsterColors.TEXT_DIM}]AI-powered end-to-end testing for web applications[/{BugsterColors.TEXT_DIM}]", justify="center")
        console.print()
        console.print(f"[{BugsterColors.TEXT_DIM}]Links:[/{BugsterColors.TEXT_DIM}]")
        console.print(f"  🌐 Dashboard: [{BugsterColors.LINK}]https://gui.bugster.dev[/{BugsterColors.LINK}]")
        console.print(f"  📚 Docs: [{BugsterColors.LINK}]https://docs.bugster.dev[/{BugsterColors.LINK}]")
        console.print(f"  🐙 GitHub: [{BugsterColors.LINK}]https://github.com/Bugsterapp/bugster-cli[/{BugsterColors.LINK}]")
        console.print()
        
        raise typer.Exit()


def configure_logging(debug: bool):
    """Configure loguru logging based on debug flag."""
    # Remove all existing handlers
    logger.remove()

    if debug:
        # Add comprehensive logging when debug is enabled
        logger.add(
            sys.stdout,
            level="DEBUG",
            filter=lambda record: record["level"].name == "DEBUG",
        )
        logger.add(
            sys.stdout,
            level="INFO",
            filter=lambda record: record["level"].name == "INFO",
        )
        logger.add(
            sys.stdout,
            level="WARNING",
            filter=lambda record: record["level"].name == "WARNING",
        )
        logger.add(
            sys.stderr,
            level="ERROR",
            filter=lambda record: record["level"].name == "ERROR",
        )

    # When debug is False, suppress all logs except CRITICAL
    # This maintains compatibility with existing patterns
    logger.add(sys.stderr, level="CRITICAL")  # Discard the message


# Global variable to track debug state for other modules
_debug_enabled = False


def is_debug_enabled() -> bool:
    """Check if debug logging is enabled."""
    return _debug_enabled


@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Print the version and exit",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
):
    f"""🐛 [bold {BugsterColors.PRIMARY}]Bugster CLI[/bold {BugsterColors.PRIMARY}] - AI-powered end-to-end testing for web applications
    
    [{BugsterColors.TEXT_DIM}]Transform your manual testing into automated test cases with intelligent code analysis.[/{BugsterColors.TEXT_DIM}]
    
    [{BugsterColors.TEXT_PRIMARY}]Quick Start:[/{BugsterColors.TEXT_PRIMARY}]
    1. [bold {BugsterColors.COMMAND}]bugster init[/bold {BugsterColors.COMMAND}]        - Initialize your project  
    2. [bold {BugsterColors.COMMAND}]bugster generate[/bold {BugsterColors.COMMAND}]    - Generate test cases
    3. [bold {BugsterColors.COMMAND}]bugster run[/bold {BugsterColors.COMMAND}]         - Run your tests
    4. [bold {BugsterColors.COMMAND}]bugster update[/bold {BugsterColors.COMMAND}]      - Update your test cases
    5. [bold {BugsterColors.COMMAND}]bugster sync[/bold {BugsterColors.COMMAND}]        - Sync your test cases with the remote repository
    
    [{BugsterColors.TEXT_DIM}]Visit [{BugsterColors.LINK}]https://gui.bugster.dev[/{BugsterColors.LINK}] to get started![/{BugsterColors.TEXT_DIM}]
    """
    global _debug_enabled
    _debug_enabled = debug
    configure_logging(debug)


@app.command()
def init():
    f"""[bold {BugsterColors.COMMAND}]Initialize[/bold {BugsterColors.COMMAND}] Bugster CLI configuration in your project.

    Set up Bugster configuration in your repository.
    Creates .bugster/ directory with project settings.
    """
    from bugster.commands.init import init_command

    init_command()


def _run_tests(
    path: Optional[str] = typer.Argument(None, help="Path to test file or directory"),
    headless: Optional[bool] = typer.Option(
        False, "--headless", help="Run tests in headless mode"
    ),
    silent: Optional[bool] = typer.Option(
        False, "--silent", "-s", help="Run in silent mode (less verbose output)"
    ),
    stream_results: Optional[bool] = typer.Option(
        False, "--stream-results", help="Stream test results as they complete"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", help="Save test results to JSON file"
    ),
    run_id: Optional[str] = typer.Option(
        None, "--run-id", help="Run ID to associate with the test run"
    ),
    base_url: Optional[str] = typer.Option(
        None, "--base-url", help="Base URL to use for the test run"
    ),
    only_affected: Optional[bool] = typer.Option(
        None, "--only-affected", help="Only run tests for affected files or directories"
    ),
):
    f"""🧪 [bold {BugsterColors.COMMAND}]Run[/bold {BugsterColors.COMMAND}] your Bugster tests
    
    Execute AI-generated test cases against your application.
    
    [{BugsterColors.TEXT_DIM}]Examples:[/{BugsterColors.TEXT_DIM}]
      [{BugsterColors.PRIMARY}]bugster run[/{BugsterColors.PRIMARY}]                    - Run all tests
      [{BugsterColors.PRIMARY}]bugster run auth/[/{BugsterColors.PRIMARY}]              - Run tests in auth/ directory  
      [{BugsterColors.PRIMARY}]bugster run --headless[/{BugsterColors.PRIMARY}]         - Run without browser UI
      [{BugsterColors.PRIMARY}]bugster run --stream-results[/{BugsterColors.PRIMARY}]   - Stream to dashboard
    """
    from bugster.commands.test import test_command

    asyncio.run(
        test_command(
            path,
            headless,
            silent,
            stream_results,
            output,
            run_id,
            base_url,
            only_affected,
        )
    )


# Register the same function with two different command names
app.command(name="test")(_run_tests)
app.command(name="run")(_run_tests)


def _analyze_codebase(
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
    f"""🔍 [bold {BugsterColors.COMMAND}]Analyze[/bold {BugsterColors.COMMAND}] your codebase
    
    Scan your application code and generate test specs.
    Uses AI to understand your app structure and create comprehensive tests.
    
    [{BugsterColors.TEXT_DIM}]This may take a few minutes for large codebases.[/{BugsterColors.TEXT_DIM}]
    """
    from bugster.commands.analyze import analyze_command

    analyze_command(options={"show_logs": show_logs, "force": force})


# Register the same function with two different command names
app.command(name="analyze")(_analyze_codebase)
app.command(name="generate")(_analyze_codebase)


@app.command()
def update(
    update_only: bool = typer.Option(
        False, help="Only update existing specs, no suggestions or deletes"
    ),
    suggest_only: bool = typer.Option(
        False, help="Only suggest new specs, no updates or deletes"
    ),
    delete_only: bool = typer.Option(
        False, help="Only delete specs, no updates or suggestions"
    ),
    show_logs: bool = typer.Option(
        False,
        "--show-logs",
        help="Show detailed logs during analysis",
    ),
):
    f"""🔄 [bold {BugsterColors.COMMAND}]Update[/bold {BugsterColors.COMMAND}] your test specs with the latest changes."""
    from bugster.commands.update import update_command

    update_command(
        update_only=update_only,
        suggest_only=suggest_only,
        delete_only=delete_only,
        show_logs=show_logs,
    )


@app.command()
def sync(
    branch: Optional[str] = typer.Option(
        None, help="Branch to sync with (defaults to current git branch or 'main')"
    ),
    pull: bool = typer.Option(False, help="Only pull specs from remote"),
    push: bool = typer.Option(False, help="Only push specs to remote"),
    clean_remote: bool = typer.Option(
        False, help="Delete remote specs that don't exist locally"
    ),
    dry_run: bool = typer.Option(
        False, help="Show what would happen without making changes"
    ),
    prefer: str = typer.Option(
        None,
        "--prefer",
        help="Prefer 'local' or 'remote' when resolving conflicts",
        click_type=click.Choice(["local", "remote"]),
    ),
):
    f"""🔄 [bold {BugsterColors.COMMAND}]Sync[/bold {BugsterColors.COMMAND}] test cases with team
    
    Keep your test cases in sync across team members and environments.
    Handles conflicts intelligently based on modification timestamps.
    """

    from bugster.commands.sync import sync_command

    sync_command(branch, pull, push, clean_remote, dry_run, prefer)


def main():
    app()


if __name__ == "__main__":
    main()
