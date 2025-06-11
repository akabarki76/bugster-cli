"""
Login command implementation for Bugster CLI.
"""

from rich.console import Console
from rich.prompt import Prompt
from bugster.utils.user_config import save_api_key
from bugster.utils.colors import BugsterColors
import webbrowser

console = Console()

DASHBOARD_URL = (
    "https://gui.bugster.dev/"  # Update this with your actual dashboard URL
)
API_KEY_HINT = "bugster_..."


def auth_command():
    # Create a styled info panel
    from rich.panel import Panel
    console.print()
    
    auth_panel = Panel(
        f"[bold]To use Bugster CLI, you need an API key from your Bugster dashboard.[/bold]\n\n"
        f"1. Visit [{BugsterColors.LINK}]https://gui.bugster.dev[/{BugsterColors.LINK}]\n"
        "2. Sign up or log in to your account\n"
        "3. Copy your API key from the dashboard\n"
        "4. Paste it below to authenticate this CLI",
        title="🚀 Getting Started",
        border_style=BugsterColors.PRIMARY,
        padding=(1, 2)
    )
    
    console.print(auth_panel)
    console.print()
    
    # Option to open browser
    if Prompt.ask(f"🌐 [{BugsterColors.TEXT_PRIMARY}]Open Bugster dashboard in your browser?[/{BugsterColors.TEXT_PRIMARY}]", choices=["y", "n"], default="y") == "y":
        console.print(f"🔍 [{BugsterColors.TEXT_DIM}]Opening https://gui.bugster.dev in your browser...[/{BugsterColors.TEXT_DIM}]")
        webbrowser.open(DASHBOARD_URL)
        console.print()
    
    # Get API key with validation
    while True:
        console.print(f"📋 [bold][{BugsterColors.TEXT_PRIMARY}]Please copy your API key from the dashboard[/{BugsterColors.TEXT_PRIMARY}][/bold]")
        console.print(f"[{BugsterColors.TEXT_DIM}]Your API key should start with 'bugster_'[/{BugsterColors.TEXT_DIM}]")
        
        api_key = Prompt.ask(f"🔑 [{BugsterColors.TEXT_PRIMARY}]Paste your API key here[/{BugsterColors.TEXT_PRIMARY}]").strip()
        
        if not api_key:
            console.print(f"❌ [{BugsterColors.ERROR}]API key cannot be empty. Please try again.[/{BugsterColors.ERROR}]")
            continue
            
        if not api_key.startswith("bugster_"):
            console.print(f"⚠️  [{BugsterColors.WARNING}]Warning: API keys typically start with 'bugster_'[/{BugsterColors.WARNING}]")
            if Prompt.ask(f"[{BugsterColors.TEXT_PRIMARY}]Continue anyway?[/{BugsterColors.TEXT_PRIMARY}]", choices=["y", "n"], default="n") == "n":
                continue
        
        # Test API key
        console.print(f"🔄 [{BugsterColors.WARNING}]Validating API key...[/{BugsterColors.WARNING}]")
        
        # Add API key validation logic here
        if validate_api_key(api_key):  # You'll need to implement this
            break
        else:
            console.print(f"❌ [{BugsterColors.ERROR}]Invalid API key. Please check and try again.[/{BugsterColors.ERROR}]")
            continue
    
    # Save API key
    try:
        save_api_key(api_key)
        console.print()
        console.print(f"✅ [bold][{BugsterColors.SUCCESS}]Authentication successful![/{BugsterColors.SUCCESS}][/bold]")
        console.print()

        
    except Exception as e:
        console.print(f"❌ [{BugsterColors.ERROR}]Error saving API key: {str(e)}[/{BugsterColors.ERROR}]")

def validate_api_key(api_key: str) -> bool:
    """Validate API key by making a test request"""
    try:
        # Add actual API validation logic here
        # For now, just check format
        return len(api_key) > 10 and api_key.startswith("bugster_")
    except Exception:
        return False