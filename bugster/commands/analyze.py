from rich.console import Console

from bugster.analyzer import analyze_codebase

# from bugster.commands.middleware import require_api_key
from bugster.libs.services.test_cases_service import TestCasesService

console = Console()


# @require_api_key
def analyze_command(options: dict = {}):
    """Run Bugster CLI analysis command."""
    console.print("🔍 Running codebase analysis...")
    analyze_codebase(options=options)
    console.print("✅ Analysis completed!")
    console.print("🚧 Running test cases generation...")
    test_cases_dir_path = TestCasesService().generate_test_cases()
    console.print("🎉 Test cases generation completed!")
    console.print(f"💾 Test cases saved to directory '{test_cases_dir_path}'")
