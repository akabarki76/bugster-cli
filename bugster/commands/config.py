"""Config command implementation for Bugster CLI."""

import re
import webbrowser
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console

from bugster.analytics import track_command
from bugster.constants import CONFIG_PATH
from bugster.utils.file import load_config

console = Console()

VERCEL_PROTECTION_URL = "https://vercel.com/d?to=%2F%5Bteam%5D%2F%5Bproject%5D%2Fsettings%2Fdeployment-protection&title=Deployment+Protection+settings"


def format_yaml_string(value: str) -> str:
    """Format a string value for YAML, adding quotes if needed."""
    if " " in value or ":" in value or value.startswith("#"):
        return f'"{value}"'
    return value


def update_vercel_bypass_secret_in_config(config_content: str, secret: str) -> str:
    """Update the Vercel bypass secret in config content while preserving comments."""
    formatted_secret = format_yaml_string(secret)
    
    # Pattern to match existing x-vercel-protection-bypass line (commented or uncommented)
    existing_pattern = r'^(\s*#?\s*x-vercel-protection-bypass:\s*).*$'
    
    # Check if the line exists
    if re.search(existing_pattern, config_content, re.MULTILINE):
        # Replace existing line
        new_content = re.sub(
            existing_pattern,
            f'x-vercel-protection-bypass: {formatted_secret}',
            config_content,
            flags=re.MULTILINE
        )
    else:
        # If no existing line found, add it after the Vercel Configuration comment section
        # This pattern matches the Vercel Configuration section and captures the entire section
        vercel_section_pattern = r'(# Vercel Configuration\n(?:# [^\n]*\n)*)'
        if re.search(vercel_section_pattern, config_content, re.MULTILINE):
            new_content = re.sub(
                vercel_section_pattern,
                f'\\1x-vercel-protection-bypass: {formatted_secret}\n',
                config_content,
                flags=re.MULTILINE
            )
        else:
            # Fallback: add at the end of the file
            new_content = config_content.rstrip() + f'\nx-vercel-protection-bypass: {formatted_secret}\n'
    
    return new_content


def validate_bypass_protection_secret(secret: str) -> bool:
    """Validate that the bypass protection secret is exactly 32 characters."""
    return len(secret) == 32


@track_command("config")
def config_command(bypass_protection: Optional[bool] = None):
    """Configure Bugster project settings."""
    from rich.prompt import Confirm, Prompt

    # Case 1: No flags provided, show help message
    if bypass_protection is None:
        console.print("Use --help to see available options.")
        return

    # Check for config file existence before proceeding
    if not CONFIG_PATH.exists():
        console.print(
            "[red]Error: Configuration file not found. Please run 'bugster init' first.[/red]"
        )
        raise typer.Exit(1)

    secret_to_save = None

    # Case 2: --bypass-protection used without a value (interactive setup)
    if bypass_protection:
        console.print("\n[bold]Vercel Protection Bypass Configuration[/bold]\n")

        if Confirm.ask(
            "Would you like to get your Vercel bypass secret now?", default=True
        ):
            console.print(
                "\n[bold cyan]Opening Vercel settings to help you find your secret...[/bold cyan]"
            )
            try:
                webbrowser.open(VERCEL_PROTECTION_URL)
                console.print(
                    f"[dim]If your browser didn't open, please visit: {VERCEL_PROTECTION_URL}[/dim]\n"
                )
            except Exception:
                console.print(
                    f"[yellow]Please visit: {VERCEL_PROTECTION_URL} to get your secret.[/yellow]\n"
                )

            secret_to_save = Prompt.ask(
                "Enter your 32-character Vercel protection bypass secret",
                password=True,
            )
        else:
            secret_to_save = Prompt.ask(
                "\nPlease enter your 32-character Vercel protection bypass secret",
                password=True,
            )
    # Case 3: --bypass-protection used with a value
    else:
        secret_to_save = bypass_protection

    # Validate and save the secret
    if not validate_bypass_protection_secret(secret_to_save):
        console.print(
            f"[red]Error: Bypass protection secret must be exactly 32 characters. "
            f"Provided secret has {len(secret_to_save)} characters.[/red]"
        )
        raise typer.Exit(1)

    try:
        # Read the current config content
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config_content = f.read()

        # Update the content while preserving comments
        updated_content = update_vercel_bypass_secret_in_config(config_content, secret_to_save)

        # Write the updated content back
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(updated_content)

        console.print(
            "\n[green]✓ Vercel protection bypass secret has been saved to config.yaml[/green]"
        )
    except Exception as e:
        console.print(f"[red]Error updating config file: {e}[/red]")
        raise typer.Exit(1) 