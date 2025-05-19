"""
Initialize command implementation.
"""

import yaml
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table

from bugster.constants import (
    BUGSTER_DIR,
    CONFIG_PATH,
    EXAMPLE_DIR,
    EXAMPLE_TEST_FILE,
    EXAMPLE_TEST,
)

console = Console()


def create_credential_entry(
    identifier="admin",
    username="admin",
    password="admin",
    description="Default admin user",
):
    """Create a credential entry with a slug identifier."""
    return {
        "id": identifier.lower().replace(" ", "-"),
        "username": username,
        "password": password,
        "description": description,
    }


def init_command():
    """Initialize Bugster CLI configuration."""
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
            description = Prompt.ask("Description", default=f"Custom user {identifier}")

            credentials.append(
                create_credential_entry(
                    identifier=identifier,
                    username=username,
                    password=password,
                    description=description,
                )
            )

            if Prompt.ask("Add another credential? (y/n)", default="n").lower() != "y":
                break
    else:
        # If no custom credentials, use default admin
        credentials.append(create_credential_entry())

    # Create folders
    EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    # Save config
    config = {"base_url": base_url, "credentials": credentials}
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # Save example test
    with open(EXAMPLE_TEST_FILE, "w") as f:
        f.write(EXAMPLE_TEST)

    # Show results
    console.print(f"[green]Configuration created at {CONFIG_PATH}")
    console.print(f"[green]Example test created at {EXAMPLE_TEST_FILE}")

    # Show credentials table
    table = Table(title="Configured Credentials")
    table.add_column("ID", style="cyan")
    table.add_column("Username", style="green")
    table.add_column("Password", style="yellow")
    table.add_column("Description", style="blue")

    for cred in credentials:
        table.add_row(
            cred["id"], cred["username"], cred["password"], cred["description"]
        )

    console.print(table)
