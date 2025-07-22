import time
import webbrowser
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from bugster.clients.http_client import BugsterHTTPClient, BugsterHTTPError
from bugster.utils.user_config import get_api_key, extract_organization_id

console = Console()


def install_github_command():
    """Install GitHub App integration."""
    # Get API key
    api_key = get_api_key()
    if not api_key:
        console.print("[red]❌ No API key found. Please run 'bugster auth' first.[/red]")
        return

    # Extract organization ID
    try:
        org_id = extract_organization_id(api_key)
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return

    # Create HTTP client
    client = BugsterHTTPClient()
    client.set_auth_header(api_key)

    try:
        # Get installation URL
        console.print("🔗 Getting GitHub installation URL...")
        installation_url = client.get(f"/api/v1/github/installations/{org_id}/setup", params={"source": "cli"})
        if not installation_url:
            console.print("[red]❌ Failed to get installation URL[/red]")
            return

        console.print(f"📂 Opening GitHub installation page in your browser...")
        console.print(f"🌐 URL: [blue]{installation_url}[/blue]")
        
        # Try to open in browser
        try:
            webbrowser.open(installation_url)
        except Exception:
            console.print("[yellow]⚠️  Could not automatically open browser. Please copy and paste the URL above.[/yellow]")

        # Poll for installation completion
        console.print("\n⏳ Waiting for GitHub installation to complete...")
        console.print("💡 Complete the installation in your browser, then return here.")

        timeout = 8 * 60  # 8 minutes in seconds
        start_time = time.time()
        poll_interval = 10  # Poll every 10 seconds

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking installation status...", total=None)
            while time.time() - start_time < timeout:
                try:
                    repos_response = client.get(f"/api/v1/github/organizations/{org_id}/repositories")
                    repositories = repos_response.get("repositories", [])
                    if repositories:
                        progress.stop()
                        console.print("\n✅ [green]GitHub installation successful![/green]")
                        console.print(f"📦 Found {len(repositories)} repositories connected.")
                        
                        # Show some repository details
                        console.print("\n📋 Connected repositories:")
                        for repo in repositories[:5]:  # Show first 5 repos
                            repo_name = repo.get("repository_name", "Unknown")
                            console.print(f"  • {repo_name}")
                        
                        if len(repositories) > 5:
                            console.print(f"  ... and {len(repositories) - 5} more")
                        
                        return

                except BugsterHTTPError:
                    # Continue polling even if there's an API error
                    pass
                except Exception:
                    # Continue polling for other errors too
                    pass

                time.sleep(poll_interval)

        # Timeout reached
        progress.stop()
        console.print("\n❌ [red]Installation timeout reached (8 minutes).[/red]")
        console.print("🔍 Something may have gone wrong during the GitHub installation.")
        console.print("🌐 Please visit [blue]https://gui.bugster.dev[/blue] to complete the GitHub integration setup manually.")

    except BugsterHTTPError as e:
        console.print(f"[red]❌ API Error during GitHub installation: {e}[/red]")
        console.print("🌐 Please visit [blue]https://gui.bugster.dev[/blue] to try installing the integration manually.")
    except Exception as e:
        console.print(f"[red]❌ Unexpected error during GitHub installation: {e}[/red]")
        console.print("🌐 Please visit [blue]https://gui.bugster.dev[/blue] to try installing the integration manually.")
    finally:
        client.close()
