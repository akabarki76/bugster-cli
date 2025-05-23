"""
Command middleware implementations.
"""

import functools
from rich.console import Console
import typer

from bugster.utils.user_config import get_api_key

console = Console()


def require_api_key(func):
    """Decorator to check if API key is set before executing a command."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        api_key = get_api_key()
        if not api_key:
            console.print(
                "[red]API key not found. Please run 'bugster login' to set up your API key.[/red]"
            )
            raise typer.Exit(1)

        return func(*args, **kwargs)

    return wrapper
