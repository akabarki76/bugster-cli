"""
Command middleware implementations.
"""

import functools
from rich.console import Console
import typer

from bugster.utils.user_config import get_api_key

console = Console()


def require_authenticated(console=None):
    """Raise an error if user is not authenticated."""
    if console is None:
        console = Console()
    
    api_key = get_api_key()
    if not api_key:
        console.print("\n❌ [red]You are not authenticated.[/red]")
        console.print("Run [bold]bugster auth[/bold] to set up your API key before using this command.\n")
        raise RuntimeError("Not authenticated")
    return api_key


def require_api_key(func):
    """Decorator to check if API key is set before executing a command."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            api_key = require_authenticated()
        except RuntimeError:
            # require_authenticated already printed the error message
            raise typer.Exit(1)

        return func(*args, **kwargs)

    return wrapper
