import typer
from rich.console import Console

from bugster.libs.services.update_service import (
    DefaultUpdateService,
    DeleteOnlyService,
    SuggestOnlyService,
    UpdateOnlyService,
)
from bugster.libs.utils.log import setup_logger

console = Console()


def update_command(
    update_only: bool = False,
    suggest_only: bool = False,
    delete_only: bool = False,
):
    """Run Bugster CLI update command."""
    conditions_sum = sum([update_only, suggest_only, delete_only])
    assert conditions_sum <= 1, (
        "At most one of update_only, suggest_only, delete_only can be True"
    )

    try:
        setup_logger()
        console.print("✓ Analyzing code changes...")

        if conditions_sum == 1:
            if update_only:
                update_service = UpdateOnlyService()
            elif suggest_only:
                update_service = SuggestOnlyService()
            elif delete_only:
                update_service = DeleteOnlyService()
        else:
            update_service = DefaultUpdateService()

        update_service.run()
    except Exception as err:
        console.print(f"[red]Error: {str(err)}[/red]")
        raise typer.Exit(1)
