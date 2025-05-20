from rich.console import Console

from bugster.analyzer import analyze_codebase
from loguru import logger
import sys

console = Console()


def analyze_command(options: dict = {}):
    """Run Bugster CLI analysis command."""
    if options.get("show_logs", False) is False:
        logger.remove()
        logger.add(sys.stderr, level="CRITICAL")

    console.print("🔍 Running codebase analysis...")
    analyze_codebase()
    console.print("✅ Analysis completed!")
