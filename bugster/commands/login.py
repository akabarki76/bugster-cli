"""
Login command implementation for Bugster CLI.
"""

from rich.console import Console
from rich.prompt import Prompt
from bugster.utils.user_config import save_api_key

console = Console()

DASHBOARD_URL = (
    "https://bugster.dev/account/api-keys"  # Update this with your actual dashboard URL
)


def login_command():
    """Handle the login command flow."""
    console.print("\n🔐 [bold]Welcome to Bugster CLI![/bold]\n")

    # Show instructions
    console.print(f"Please visit this URL to generate your API key:")
    console.print(f"[link]{DASHBOARD_URL}[/link]\n")

    # Get API key from user
    api_key = Prompt.ask("👉 Paste your API key here")

    # Basic validation
    if not api_key.strip():
        console.print("\n❌ [red]Error: API key cannot be empty[/red]")
        return

    # Save the API key
    try:
        save_api_key(api_key.strip())
        console.print("\n✅ [green]API key saved successfully![/green]")
        console.print("\nYou can now use Bugster CLI. Try running:")
        console.print("[bold]  $ bugster init[/bold]")
    except Exception as e:
        console.print(f"\n❌ [red]Error saving API key: {str(e)}[/red]")
