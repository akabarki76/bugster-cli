"""
Onboarding utilities for Bugster CLI.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from bugster.utils.user_config import get_api_key

console = Console()

DOCS_URL = "https://docs.bugster.dev"

def is_project_initialized() -> bool:
    """Check if the project is initialized."""
    return Path(".bugster").exists()

def get_next_step() -> Optional[str]:
    """Get the next step in the onboarding flow."""
    if not get_api_key():
        return "auth"
    if not is_project_initialized():
        return "init"
    return None

def print_welcome(show_full_help: bool = False) -> None:
    """Print the welcome message and onboarding flow."""
    if not show_full_help:
        # For empty command, show welcome first
        welcome = Text("🦑 Welcome to Bugster — Find real bugs before your users do.\n", style="bold cyan")
        console.print(welcome)
    
    # Get user status
    next_step = get_next_step()
    
    # Create quickstart panel content
    steps = [
        ("bugster auth", "Authenticate", "blue"),
        ("bugster init", "Initialize", "green"),
        ("bugster analyze", "Analyze", "magenta"),
        ("bugster test", "Run", "yellow")
    ]

    # Print quickstart section
    if show_full_help:
        console.print("\n╭─ Quickstart ────────────────────────────────────────────────────╮")
    else:
        console.print("\nQuickstart:")
        
    for cmd, verb, color in steps:
        # Create styled command and verb
        cmd_text = Text(cmd, style="cyan")
        verb_text = Text(verb, style=color)
        # Add padding manually
        padding = " " * (20 - len(cmd))
        # Print command and description
        if show_full_help:
            console.print(f"│ {cmd_text}{padding}{verb_text} Bugster tests.")
        else:
            console.print(f"  {cmd_text}{padding}{verb_text} Bugster tests.")

    if show_full_help:
        console.print("╰──────────────────────────────────────────────────────────────────╯\n")
    
    # Print next step if needed and not in help mode
    if next_step and not show_full_help:
        console.print(f"\nNext: {Text(f'bugster {next_step}', style='bold green')}")
        console.print(f"\nDocs: {DOCS_URL} ")