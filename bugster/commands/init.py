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
    CONFIG_PATH,
    EXAMPLE_DIR,
    EXAMPLE_TEST_FILE,
    EXAMPLE_TEST,
)
from bugster.utils.user_config import get_api_key
from bugster.clients.http_client import BugsterHTTPClient, BugsterHTTPError
from bugster.commands.auth import auth_command
from bugster.utils.colors import BugsterColors

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


def find_existing_config():
    """Find existing configuration in current or parent directories."""
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:  # Stop at root directory
        config_path = current_dir / ".bugster" / "config.yaml"
        if config_path.exists():
            return True, config_path
        current_dir = current_dir.parent
    return False, None


def update_gitignore():
    """Update .gitignore with Bugster entries."""
    gitignore_path = Path(".gitignore")
    bugster_entries = [
        "# Bugster",
        ".bugster/results/",
        ".bugster/screenshots/",
        ".bugster/videos/",
        ".bugster/logs/",
        ".bugster/reports/",
        "*.bugster.log",
    ]

    # Read existing entries
    existing_entries = []
    if gitignore_path.exists():
        with open(gitignore_path) as f:
            existing_entries = f.read().splitlines()

    # Add missing entries
    with open(gitignore_path, "a") as f:
        if existing_entries and existing_entries[-1] != "":
            f.write("\n")  # Add newline if file doesn't end with one

        for entry in bugster_entries:
            if entry not in existing_entries:
                f.write(f"{entry}\n")


def generate_project_id(project_name: str) -> str:
    """Generate a project ID from project name."""
    # Use timestamp to ensure uniqueness
    timestamp = int(time.time())
    # Convert project name to lowercase and replace spaces with dashes
    safe_name = project_name.lower().replace(" ", "-")
    return f"{safe_name}-{timestamp}"


def init_command():
    """Initialize Bugster CLI configuration."""
    
    console.print()
    console.print(f"🚀 [{BugsterColors.TEXT_PRIMARY}]Welcome to Bugster![/{BugsterColors.TEXT_PRIMARY}]")
    console.print(f"[{BugsterColors.TEXT_DIM}]Let's set up your project[/{BugsterColors.TEXT_DIM}]\n")
    
    # First check if user is authenticated
    api_key = get_api_key()
    if not api_key:
        console.print(f"⚠️  [{BugsterColors.WARNING}]Authentication Required[/{BugsterColors.WARNING}]")
        console.print(f"[{BugsterColors.TEXT_DIM}]First, let's set up your API key[/{BugsterColors.TEXT_DIM}]\n")
        
        # Run auth command
        auth_command()
        
        # Check if auth was successful
        api_key = get_api_key()
        if not api_key:
            console.print(f"\n❌ [{BugsterColors.ERROR}]Authentication failed. Please try again.[/{BugsterColors.ERROR}]")
            raise typer.Exit(1)
        
        console.print(f"\n✅ [{BugsterColors.SUCCESS}]Authentication successful![/{BugsterColors.SUCCESS}]")
        console.print(f"[{BugsterColors.TEXT_DIM}]Now let's configure your project[/{BugsterColors.TEXT_DIM}]\n")

    # Check for existing configuration in current or parent directories
    config_exists, existing_config_path = find_existing_config()
    
    if config_exists:
        if existing_config_path == CONFIG_PATH:
            if not Confirm.ask(
                f"⚠️  [{BugsterColors.WARNING}]Existing Bugster project detected. Would you like to reinitialize? This will overwrite current settings[/{BugsterColors.WARNING}]",
                default=False
            ):
                console.print(f"\n❌ [{BugsterColors.WARNING}]Initialization cancelled[/{BugsterColors.WARNING}]")
                raise typer.Exit(0)
        else:
            current_dir = Path.cwd()
            project_dir = existing_config_path.parent.parent  # Go up two levels: .bugster/config.yaml -> .bugster -> project_dir
            console.print(f"\n🚫 [{BugsterColors.ERROR}]Cannot initialize nested Bugster project[/{BugsterColors.ERROR}]")
            console.print(f"📁 [{BugsterColors.WARNING}]Current directory:[/{BugsterColors.WARNING}] {current_dir}")
            console.print(f"📁 [{BugsterColors.WARNING}]Parent project:[/{BugsterColors.WARNING}] {project_dir}")
            console.print(f"\n💡 [{BugsterColors.ERROR}]Please initialize the project outside of any existing Bugster project[/{BugsterColors.ERROR}]")
            raise typer.Exit(1)

    # Project setup
    console.print(f"\n📝 [{BugsterColors.TEXT_PRIMARY}]Project Setup[/{BugsterColors.TEXT_PRIMARY}]")
    console.print(f"[{BugsterColors.TEXT_DIM}]Let's configure your project details[/{BugsterColors.TEXT_DIM}]\n")
    
    project_name = Prompt.ask(f"🏷️  [{BugsterColors.TEXT_PRIMARY}]Project name[/{BugsterColors.TEXT_PRIMARY}]", default="My Project")
    
    # Get project ID from API
    try:
        with BugsterHTTPClient() as client:
            # Set the API key header
            client.set_headers({"x-api-key": api_key})
            
            console.print(f"\n[{BugsterColors.TEXT_DIM}]Creating project on Bugster...[/{BugsterColors.TEXT_DIM}]")
            
            # Make the POST request
            project_data = client.post(
                "/api/v1/gui/project",
                json={"name": project_name}
            )
            
            project_id = project_data.get("project_id") or project_data.get("id")
            
            if not project_id:
                console.print(f"[{BugsterColors.ERROR}]Error: Project ID not found in API response[/{BugsterColors.ERROR}]")
                raise typer.Exit(1)
                
            console.print(f"✨ [{BugsterColors.SUCCESS}]Project created successfully![/{BugsterColors.SUCCESS}]")
            
    except BugsterHTTPError as e:
        console.print(f"⚠️  [{BugsterColors.ERROR}]API connection error: {str(e)}[/{BugsterColors.ERROR}]")
        console.print(f"↪️  [{BugsterColors.WARNING}]Falling back to local project ID[/{BugsterColors.WARNING}]")
        project_id = generate_project_id(project_name)
    except Exception as e:
        console.print(f"⚠️  [{BugsterColors.ERROR}]Unexpected error: {str(e)}[/{BugsterColors.ERROR}]")
        console.print(f"↪️  [{BugsterColors.WARNING}]Falling back to local project ID[/{BugsterColors.WARNING}]")
        project_id = generate_project_id(project_name)

    console.print(f"\n🆔 Project ID: [{BugsterColors.INFO}]{project_id}[/{BugsterColors.INFO}]")
    
    base_url = Prompt.ask(f"\n🌐 [{BugsterColors.TEXT_PRIMARY}]Application URL[/{BugsterColors.TEXT_PRIMARY}]", default="http://localhost:3000")

    # Initialize empty credentials array
    credentials = []

    console.print(f"\n🔐 [{BugsterColors.TEXT_PRIMARY}]Authentication Setup[/{BugsterColors.TEXT_PRIMARY}]")
    console.print(f"[{BugsterColors.TEXT_DIM}]Configure login credentials for your application[/{BugsterColors.TEXT_DIM}]\n")

    if Prompt.ask(f"➕ [{BugsterColors.TEXT_PRIMARY}]Would you like to add custom login credentials? (y/n)[/{BugsterColors.TEXT_PRIMARY}]", default="y").lower() == "y":
        while True:
            identifier = Prompt.ask(
                f"👤 [{BugsterColors.TEXT_PRIMARY}]Credential name (e.g. admin-user, test-manager)[/{BugsterColors.TEXT_PRIMARY}]",
                default="admin",
            )
            username = Prompt.ask(f"📧 [{BugsterColors.TEXT_PRIMARY}]Username/Email[/{BugsterColors.TEXT_PRIMARY}]")
            password = Prompt.ask(f"🔒 [{BugsterColors.TEXT_PRIMARY}]Password[/{BugsterColors.TEXT_PRIMARY}]", password=True)

            credentials.append(
                create_credential_entry(
                    identifier=identifier,
                    username=username,
                    password=password,
                )
            )
            console.print(f"✓ [{BugsterColors.SUCCESS}]Credential added successfully[/{BugsterColors.SUCCESS}]\n")
            
            if not Prompt.ask(f"➕ [{BugsterColors.TEXT_PRIMARY}]Add another credential? (y/n)[/{BugsterColors.TEXT_PRIMARY}]", default="n").lower() == "y":
                break

    else:
        # If no custom credentials, use default admin
        credentials.append(create_credential_entry())
        console.print(f"ℹ️  [{BugsterColors.TEXT_DIM}]Using default credentials (admin/admin)[/{BugsterColors.TEXT_DIM}]\n")

    # Create project structure
    console.print(f"🏗️  [{BugsterColors.TEXT_PRIMARY}]Setting Up Project Structure[/{BugsterColors.TEXT_PRIMARY}]")
    console.print(f"[{BugsterColors.TEXT_DIM}]Creating necessary files and directories[/{BugsterColors.TEXT_DIM}]\n")

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
    console.print(f"\n🎉 [{BugsterColors.SUCCESS}]Project Initialized Successfully![/{BugsterColors.SUCCESS}]")
    
    # Project summary
    table = Table(
        title="📋 Project Summary",
        show_header=True,
        header_style=BugsterColors.INFO
    )
    table.add_column("Setting", style=BugsterColors.INFO)
    table.add_column("Value", style=BugsterColors.SUCCESS)
    
    table.add_row("Project Name", project_name)
    table.add_row("Project ID", project_id)
    table.add_row("Base URL", base_url)
    table.add_row("Config Location", str(CONFIG_PATH))
    table.add_row("Example Test", str(EXAMPLE_TEST_FILE))
    table.add_row("Credentials", f"{len(credentials)} configured")
    
    console.print()
    console.print(table)

    # Show credentials table only if custom credentials were added
    if len(credentials) > 1 or (len(credentials) == 1 and credentials[0] != create_credential_entry()):
        creds_table = Table(title="🔐 Configured Credentials")
        creds_table.add_column("ID", style=BugsterColors.INFO)
        creds_table.add_column("Username", style=BugsterColors.SUCCESS)
        creds_table.add_column("Password", style=BugsterColors.WARNING)

        for cred in credentials:
            password_masked = "•" * len(cred["password"])
            creds_table.add_row(cred["id"], cred["username"], password_masked)

        console.print()
        console.print(creds_table)
    
    # Next steps panel
    from rich.panel import Panel
    
    success_panel = Panel(
            f"[bold][{BugsterColors.SUCCESS}]🎉 You're all set![/{BugsterColors.SUCCESS}][/bold]\n\n"
            f"[bold][{BugsterColors.TEXT_PRIMARY}]Next steps:[/{BugsterColors.TEXT_PRIMARY}][/bold]\n"
            f"1. [{BugsterColors.COMMAND}]bugster generate[/{BugsterColors.COMMAND}] - Generate test specs\n"
            f"2. [{BugsterColors.COMMAND}]bugster run[/{BugsterColors.COMMAND}] - Run your specs\n"
            f"3. [{BugsterColors.TEXT_DIM}]Integrate Bugster with GitHub[{BugsterColors.LINK}]https://gui.bugster.dev/dashboard[/{BugsterColors.LINK}][/{BugsterColors.TEXT_DIM}]\n\n"
            f"[{BugsterColors.TEXT_DIM}]Need help? Visit [{BugsterColors.LINK}]https://docs.bugster.dev[/{BugsterColors.LINK}][/{BugsterColors.TEXT_DIM}]",
            title="🚀 Ready to Go",
            border_style=BugsterColors.SUCCESS
        )
    console.print()
    console.print(success_panel)
    console.print()
