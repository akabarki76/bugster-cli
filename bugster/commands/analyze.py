from rich.console import Console

from bugster.analyzer import analyze_codebase
from bugster.commands.middleware import require_api_key

console = Console()


@require_api_key
def analyze_command(options: dict = {}):
    """Run Bugster CLI analysis command."""
    console.print("🔍 Running codebase analysis...")
    analyze_codebase(options=options)
    console.print("✅ Analysis completed!")
