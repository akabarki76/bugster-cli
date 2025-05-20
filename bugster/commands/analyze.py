from rich.console import Console

from bugster.analyzer import analyze_codebase

console = Console()


def analyze_command():
    """Run analysis on the codebase."""
    console.print("🔍 Running codebase analysis...")
    analyze_codebase()
    console.print("✅ Analysis completed!")