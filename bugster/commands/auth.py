"""Login command implementation for Bugster CLI."""

import webbrowser

from rich.console import Console
from rich.prompt import Prompt

from src.utils.user_config import save_api_key

console = Console()

DASHBOARD_URL = "https://gui.src.dev/"  # Update this with your actual dashboard URL
API_KEY_HINT = "bugster_..."


def auth_command():
    console.print("\n🔐 [bold cyan]Welcome to Bugster CLI[/bold cyan]\n")
    console.print(
        "To use Bugster CLI, you'll need an API key. "
        "Generate it from your [bold][link]%s[/link][/bold]." % DASHBOARD_URL
    )
    console.print(
        "\n[dim]Tip: In the dashboard, navigate to Dashboard > API Keys.[/dim]\n"
    )
    if (
        Prompt.ask(
            "🌐 Open the dashboard in your browser now? (y/N)", default="N"
        ).lower()
        == "y"
    ):
        webbrowser.open(DASHBOARD_URL)

    # Prompt for API key
    api_key = Prompt.ask(f"👉 Paste your API key (hint: {API_KEY_HINT})").strip()

    # Validate
    if not api_key:
        console.print("\n❌ [red]API key cannot be empty.[/red]")
        return
    if not api_key.startswith("bugster_"):
        console.print(
            "\n⚠️ [yellow]Warning: API keys should start with 'bugster_'. Please double-check.[/yellow]"
        )

    # Save
    try:
        save_api_key(api_key)
        console.print("\n✅ [green]API key saved! You're ready to go.[/green]")
        console.print("[dim]Try: [bold]bugster init[/bold][/dim]")
    except Exception as e:
        console.print(f"\n❌ [red]Error saving API key: {str(e)}[/red]")
