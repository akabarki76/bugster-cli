import os
import yaml
import typer
from rich.prompt import Prompt
from rich.console import Console
from pathlib import Path

app = typer.Typer()
console = Console()

BUGSTER_DIR = Path.cwd() / ".bugster"
CONFIG_PATH = BUGSTER_DIR / "config.yaml"
TESTS_DIR = BUGSTER_DIR / "tests"
EXAMPLE_DIR = TESTS_DIR / "example"
EXAMPLE_TEST_FILE = EXAMPLE_DIR / "tests.yaml"

EXAMPLE_TEST = """# @META:{\"id\":\"97e3fc25-bc8d-42e6-aece-0d9205fd1abc\",\"version\":1}
# This comment contains machine-readable metadata that should not be modified
- name: Checkout Process Test
  task: Verify that users can complete the checkout process
  expected_result: Order should be successfully placed
  steps:
    - Navigate to /products page
    - Click on \"Buy Now\" button for the \"Pro\" plan
    - Fill in the checkout form with valid information
    - Click on \"Place Order\" button
    - Verify that the order is successfully placed
    - Check the order confirmation page for success message
    - Check the order details in the database
    - Verify that the user has been subscribed to the \"Pro\" plan
    - Verify that the user has been redirected to the /flows page
    - Verify that the user has been redirected to the /flows page
    - Verify that the user has been redirected to the /flows page
    - Verify that the user has been redirected to the /flows page
    - Verify that the user has been redirected to the /flows page
"""


def init_command():
    """Initialize Bugster CLI configuration."""
    base_url = Prompt.ask("Base URL", default="http://localhost:3000")
    if Prompt.ask("Do you want to add credentials? (y/n)", default="n").lower() == "y":
        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)
        credentials = {"username": username, "password": password}
    else:
        credentials = None

    # Create folders
    EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    # Save config
    config = {"base_url": base_url}
    if credentials:
        config["credentials"] = credentials
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f)
    # Save example test
    with open(EXAMPLE_TEST_FILE, "w") as f:
        f.write(EXAMPLE_TEST)
    console.print(f"[green]Configuration created at {CONFIG_PATH}")
    console.print(f"[green]Example test created at {EXAMPLE_TEST_FILE}")


@app.command()
def init():
    """Initialize Bugster CLI configuration."""
    init_command()


def main():
    app()


if __name__ == "__main__":
    main()
