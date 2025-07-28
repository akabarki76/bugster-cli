import time
import webbrowser
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

from bugster.clients.http_client import BugsterHTTPClient, BugsterHTTPError
from bugster.utils.user_config import get_api_key, extract_organization_id
from bugster.utils.file import load_config

console = Console()


def select_repository_for_integration(installation_id, repositories, client, org_id, api_key):
    """Allow user to select a repository for integration with Bugster."""
    console.print("\n🎯 [bold]Select a repository to integrate with Bugster:[/bold]")
    console.print("📋 Available repositories:")
    
    # Display numbered list of repositories
    for i, repo in enumerate(repositories, 1):
        repo_name = repo.get("repository_name", "Unknown")
        repo_full_name = repo.get("repository_full_name", "Unknown")
        console.print(f"  {i}. {repo_full_name}")
    
    # Get user selection
    while True:
        try:
            choice = Prompt.ask(
                f"\n🔢 Enter your choice (1-{len(repositories)})",
                default="1"
            )
            choice_index = int(choice) - 1
            
            if 0 <= choice_index < len(repositories):
                selected_repo = repositories[choice_index]
                break
            else:
                console.print(f"[red]❌ Please enter a number between 1 and {len(repositories)}[/red]")
        except ValueError:
            console.print("[red]❌ Please enter a valid number[/red]")
    
    # Get project_id from config.yaml
    try:
        config = load_config()
        project_id = config.project_id
    except Exception as e:
        console.print(f"[red]❌ Error loading project_id from config: {e}[/red]")
        console.print("[yellow]💡 Please run 'bugster init' to set up your project configuration.[/yellow]")
        return False
    
    # Prepare data for API call
    repo_data = {
        "repository_id": str(selected_repo.get("repository_id")),
        "organization_id": org_id,
        "installation_id": installation_id,
        "repository_full_name": selected_repo.get("repository_full_name"),
        "project_id": project_id
    }
    
    console.print(f"\n🚀 Integrating repository: [blue]{selected_repo.get('repository_full_name', 'Unknown')}[/blue]")
    
    try:
        # Send POST request to integrate the repository
        response = client.post("/api/v1/github/projects/repositories", json=repo_data)
        
        console.print("✅ [green]Repository successfully integrated with Bugster![/green]")
        console.print(f"📦 Repository: {selected_repo.get('repository_full_name', 'Unknown')}")
        
        return True
        
    except BugsterHTTPError as e:
        console.print(f"[red]❌ Failed to integrate repository: {e}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Unexpected error during repository integration: {e}[/red]")
        return False


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
                    installation_id = repos_response.get("installation_id", "")
                    if repositories:
                        progress.stop()
                        console.print("\n✅ [green]GitHub installation successful![/green]")
                        console.print(f"📦 Found {len(repositories)} repositories connected.")
                        
                        # Allow user to select a repository for integration
                        integration_success = select_repository_for_integration(installation_id,repositories, client, org_id, api_key)
                        
                        if integration_success:
                            console.print("\n🎉 [green]GitHub integration completed successfully![/green]")
                        else:
                            console.print("\n⚠️  [yellow]GitHub app installed but repository integration failed.[/yellow]")
                            console.print("🌐 You can try again later or visit [blue]https://gui.bugster.dev[/blue] to complete the setup manually.")
                        
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
