from rich.console import Console

from bugster.analyzer import analyze_codebase

console = Console()


def analyze_command(options: dict = {}):
    """Run Bugster CLI analysis command."""
    console.print("🔍 Running codebase analysis...")
    analyze_codebase(options=options)
    console.print("✅ Analysis completed!")
