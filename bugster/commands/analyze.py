import os

import typer
from rich.console import Console
from rich.status import Status

from bugster.analytics import track_command
from bugster.analyzer import analyze_codebase
from bugster.analyzer.utils.analysis_tracker import (
    analysis_tracker,
    has_analysis_completed,
)
from bugster.clients.http_client import BugsterHTTPClient
from bugster.commands.middleware import require_api_key
from bugster.constants import TESTS_DIR, WORKING_DIR
from bugster.libs.services.test_cases_service import TestCasesService
from bugster.utils.user_config import get_api_key

console = Console()


def has_yaml_test_cases() -> bool:
    """Check if there are any YAML test case files in the TESTS_DIR."""
    if not TESTS_DIR.exists():
        return False

    # Look for .yaml or .yml files recursively in TESTS_DIR
    for file_path in TESTS_DIR.rglob("*.yaml"):
        if file_path.is_file():
            return True

    for file_path in TESTS_DIR.rglob("*.yml"):
        if file_path.is_file():
            return True

    return False


@require_api_key
@track_command("generate")
def analyze_command(options: dict = {}):
    """Run Bugster CLI analysis command."""
    force = options.get("force", False)
    page_filter = options.get("page_filter")
    count = options.get("count")

    try:
        if has_analysis_completed() and not force:
            console.print(
                "🔒 The codebase has already been analyzed and cannot be run again"
            )
            return

        with analysis_tracker():
            console.print("🔍 Starting analysis...")

            with Status(" Analyzing codebase...", spinner="dots") as status:
                analyze_codebase(options=options)
                status.stop()
                console.print("✅ Analysis completed!")

            TestCasesService().generate_test_cases(page_filter=page_filter, count=count)
            console.print()

            if page_filter:
                console.print("📁 Test specs generated only for files:")

                for file_path in page_filter:
                    console.print(f"   {file_path}")

                console.print("\nSpecs saved to:")
                console.print(f"   {os.path.relpath(TESTS_DIR, WORKING_DIR)}")
            else:
                console.print("📁 Test specs saved to:")
                console.print(f"   {os.path.relpath(TESTS_DIR, WORKING_DIR)}")

            if not has_yaml_test_cases():
                with BugsterHTTPClient() as client:
                    client.set_headers({"x-api-key": get_api_key()})
                    client.patch(
                        "/api/v1/users/me/onboarding-status",
                        json={"generate": "completed"},
                    )
    except Exception as err:
        console.print(f"[red]Error: {str(err)}[/red]")
        raise typer.Exit(1)
