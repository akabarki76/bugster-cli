import typer
from rich.console import Console
from rich.status import Status

from bugster.analyzer import analyze_codebase
from bugster.analyzer.utils.analysis_tracker import (
    analysis_tracker,
    has_analysis_completed,
)
from bugster.analytics import track_command
from bugster.commands.middleware import require_api_key
from bugster.constants import TESTS_DIR
from bugster.libs.services.test_cases_service import TestCasesService

console = Console()


@require_api_key
@track_command("generate")
def analyze_command(options: dict = {}):
    """Run Bugster CLI analysis command."""
    force = options.get("force", False)
    
    try:
        if has_analysis_completed() and not force:
            console.print(
                "🔒 The codebase has already been analyzed and cannot be run again"
            )
            return
        with analysis_tracker():
            console.print("🔍 Running codebase analysis...")

            with Status(" Analyzing codebase...", spinner="dots") as status:
                analyze_codebase(options=options) 
                status.stop()
                console.print("✅ Analysis completed!")

            with Status(" Generating test cases...", spinner="dots") as status:
                TestCasesService().generate_test_cases()
                status.stop()
                console.print("🎉 Test cases generation completed!")

            console.print(f"💾 Test cases saved to directory '{TESTS_DIR}'")
    except Exception as err:
        console.print(f"[red]Error: {str(err)}[/red]")
        raise typer.Exit(1)
