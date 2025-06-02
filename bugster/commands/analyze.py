import typer
from rich.console import Console
from rich.status import Status

from bugster.analyzer import analyze_codebase

# from bugster.commands.middleware import require_api_key
from bugster.libs.services.test_cases_service import TestCasesService

console = Console()


# @require_api_key
def analyze_command(options: dict = {}):
    """Run Bugster CLI analysis command."""
    try:
        console.print("🔍 Running codebase analysis...")

        with Status(" Analyzing codebase...", spinner="dots") as status:
            analyze_codebase(options=options)
            status.stop()
            console.print("✅ Analysis completed!")

        with Status(" Generating test cases...", spinner="dots") as status:
            test_cases_dir_path = TestCasesService().generate_test_cases()
            status.stop()
            console.print("🎉 Test cases generation completed!")

        console.print(f"💾 Test cases saved to directory '{test_cases_dir_path}'")
    except Exception as err:
        console.print(f"[red]Error: {str(err)}[/red]")
        raise typer.Exit(1)
