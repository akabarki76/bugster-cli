"""
File utility functions for Bugster.
"""

from pathlib import Path
from typing import Optional, List
import yaml
import typer
from rich.console import Console
import json
import tempfile

from bugster.constants import CONFIG_PATH, TESTS_DIR
from bugster.types import Config

console = Console()


async def load_config() -> Config:
    """Load configuration from config.yaml"""
    if not CONFIG_PATH.exists():
        console.print(
            "[red]Error: Configuration file not found. Please run 'bugster init' first.[/red]"
        )
        raise typer.Exit(1)

    with open(CONFIG_PATH) as f:
        return Config(**yaml.safe_load(f))


async def load_test_files(test_path: Optional[Path] = None) -> List[dict]:
    """Load test files from the given path or all tests if no path specified."""
    test_files = []

    if test_path is None:
        test_path = TESTS_DIR

    if not test_path.exists():
        console.print(f"[red]Error: Path {test_path} does not exist[/red]")
        raise typer.Exit(1)

    if test_path.is_file():
        if test_path.suffix == ".yaml":
            with open(test_path) as f:
                test_files.append({"file": test_path, "content": yaml.safe_load(f)})
    else:
        # Recursively find all .yaml files
        for file in test_path.rglob("*.yaml"):
            with open(file) as f:
                test_files.append({"file": file, "content": yaml.safe_load(f)})

    return test_files


def get_mcp_config_path(mcp_config: dict, version: str) -> str:
    """Get the MCP config file path. Creates a temporary config file with browser settings."""

    # Create a temporary file with a specific name
    temp_dir = tempfile.gettempdir()
    config_path = Path(temp_dir) / f"bugster_mcp_{version}.config.json"

    # Only create the file if it doesn't exist
    if not config_path.exists():
        # Write the configuration
        with open(config_path, "w") as f:
            json.dump(mcp_config, f, indent=2)

    return str(config_path)
