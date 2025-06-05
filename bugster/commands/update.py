import typer
from rich.console import Console

from bugster.commands.middleware import require_api_key
from bugster.libs.services.update_service import (
    get_update_service,
)
from bugster.libs.utils.log import setup_logger

console = Console()


@require_api_key
def update_command(
    update_only: bool = False,
    suggest_only: bool = False,
    delete_only: bool = False,
    show_logs: bool = False,
):
    """Run Bugster CLI update command."""
    assert sum([update_only, suggest_only, delete_only]) <= 1, (
        "At most one of update_only, suggest_only, delete_only can be True"
    )

    try:
        setup_logger(show_logs=show_logs)
        console.print("✓ Analyzing code changes...")
        update_service = get_update_service(
            update_only=update_only, suggest_only=suggest_only, delete_only=delete_only
        )
        update_service.run()
    except Exception as err:
        console.print(f"[red]Error: {str(err)}[/red]")
        raise typer.Exit(1)
