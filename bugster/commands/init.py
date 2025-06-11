"""
Initialize command implementation.
"""

import yaml
import time
import os
from pathlib import Path
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.table import Table
import typer

from bugster.constants import (
    BUGSTER_DIR,
    CONFIG_PATH,
    EXAMPLE_DIR,
    EXAMPLE_TEST_FILE,
    EXAMPLE_TEST,
)
from bugster.commands.middleware import require_api_key
from bugster.utils.user_config import get_api_key
from bugster.clients.http_client import BugsterHTTPClient, BugsterHTTPError

console = Console()


def create_credential_entry(
    identifier="admin",
    username="admin",
    password="admin",
):
    """Create a credential entry with a slug identifier."""
    return {
        "id": identifier.lower().replace(" ", "-"),
        "username": username,
        "password": password,
    }


def generate_project_id(name):
    """Generate a unique project ID from the project name.

    Combines the slugified project name with a timestamp to ensure uniqueness.
    """
    slug = name.lower().replace(" ", "-")
    timestamp = str(int(time.time()))
    return f"{slug}-{timestamp}"


def update_gitignore():
    """Create or update .gitignore to ignore videos, next, and example directories."""
    gitignore_path = BUGSTER_DIR / ".gitignore"
    ignore_patterns = [
        "videos/",
        "next/",
        "project.json",
    ]

    # Check if .gitignore exists
    if os.path.exists(gitignore_path):
        # Read existing content
        with open(gitignore_path, "r") as f:
            content = f.read()

        # Check which patterns need to be added
        patterns_to_add = []
        for pattern in ignore_patterns:
            if pattern not in content:
                patterns_to_add.append(pattern)

        # Add missing patterns
        if patterns_to_add:
            with open(gitignore_path, "a") as f:
                if not content.endswith("\n"):
                    f.write("\n")
                for pattern in patterns_to_add:
                    f.write(f"{pattern}\n")
    else:
        # Create new .gitignore with all patterns
        with open(gitignore_path, "w") as f:
            for pattern in ignore_patterns:
                f.write(f"{pattern}\n")


def find_existing_config():
    """Check for existing Bugster configuration in current or parent directories.
    
    Returns:
        tuple: (exists: bool, config_path: Path) - Whether config exists and its path
    """
    current = Path.cwd()
    
    # Check all parent directories up to root
    while current != current.parent:
        config_path = current / '.bugster' / 'config.yaml'
        if config_path.exists():
            return True, config_path
        current = current.parent
    
    return False, None


@require_api_key
def init_command():
    """Initialize Bugster CLI configuration."""
    # Check for existing configuration in current or parent directories
    config_exists, existing_config_path = find_existing_config()
    
    if config_exists:
        if existing_config_path == CONFIG_PATH:
            if not Confirm.ask("There is a project in the repository, are you sure to initialize again? This action will remove the current configuration of the project", default=False):
                console.print("[yellow]Initialization cancelled.[/yellow]")
                raise typer.Exit(0)
        else:
            current_dir = Path.cwd()
            project_dir = existing_config_path.parent.parent  # Go up two levels: .bugster/config.yaml -> .bugster -> project_dir
            console.print(f"\n[red]Error: Cannot initialize a new project inside an existing Bugster project.[/red]")
            console.print(f"[yellow]Current directory:[/yellow] {current_dir}")
            console.print(f"[yellow]Existing project directory:[/yellow] {project_dir}")
            console.print("\n[red]Please initialize the project in a directory that is not inside an existing Bugster project.[/red]")
            raise typer.Exit(1)

    # Ask for project name
    project_name = Prompt.ask("Project name", default="My Project")
    
    # Get project ID from API
    try:
        api_key = get_api_key()
        
        with BugsterHTTPClient() as client:
            # Set the API key header
            client.set_headers({"x-api-key": api_key})
            
            # Make the POST request
            project_data = client.post(
                "/api/v1/gui/project",
                json={"name": project_name}
            )
            
            project_id = project_data.get("project_id") or project_data.get("id")
            
            if not project_id:
                console.print("[red]Error: Project ID not found in API response[/red]")
                raise typer.Exit(1)
                
    except BugsterHTTPError as e:
        console.print(f"[red]Error creating project via API: {str(e)}[/red]")
        console.print("[yellow]Falling back to local project ID generation[/yellow]")
        project_id = generate_project_id(project_name)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        console.print("[yellow]Falling back to local project ID generation[/yellow]")
        project_id = generate_project_id(project_name)

    base_url = Prompt.ask("Base URL", default="http://localhost:3000")

    # Initialize empty credentials array
    credentials = []

    if Prompt.ask("Do you want to add credentials? (y/n)", default="n").lower() == "y":
        while True:
            identifier = Prompt.ask(
                "Credential identifier (e.g. admin-user, test-manager)",
                default="custom-user",
            )
            username = Prompt.ask("Username")
            password = Prompt.ask("Password", password=True)

            credentials.append(
                create_credential_entry(
                    identifier=identifier,
                    username=username,
                    password=password,
                )
            )
            break

    else:
        # If no custom credentials, use default admin
        credentials.append(create_credential_entry())

    # Create folders
    EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    # Update .gitignore
    update_gitignore()

    # Save config
    config = {
        "project_name": project_name,
        "project_id": project_id,
        "base_url": base_url,
        "credentials": credentials,
    }
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # Save example test
    with open(EXAMPLE_TEST_FILE, "w") as f:
        f.write(EXAMPLE_TEST)

    # Show results
    console.print(f"[green]Configuration created at {CONFIG_PATH}")
    console.print(f"[green]Example test created at {EXAMPLE_TEST_FILE}")

    # Show credentials table only if custom credentials were added
    if len(credentials) > 1 or (len(credentials) == 1 and credentials[0] != create_credential_entry()):
        table = Table(title="Configured Credentials")
        table.add_column("ID", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Password", style="yellow")

        for cred in credentials:
            table.add_row(cred["id"], cred["username"], cred["password"])

        console.print(table)
