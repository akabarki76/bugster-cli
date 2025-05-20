from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.style import Style
from typing import Optional, List

from bugster.clients.ws_client import WebSocketClient
from bugster.clients.mcp_client import MCPStdioClient
from bugster.utils.file import load_config, load_test_files
from bugster.types import (
    Config,
    NamedTestResult,
    Test,
    WebSocketCompleteMessage,
    WebSocketInitTestMessage,
    WebSocketStepRequestMessage,
    WebSocketStepResultMessage,
)

console = Console()


def create_results_table(results: List[NamedTestResult]) -> Table:
    """Create a formatted table with test results."""
    table = Table(title="Test Results")
    table.add_column("Name", justify="left")
    table.add_column("Result", justify="left")
    table.add_column("Reason", justify="left")

    for result in results:
        table.add_row(
            result.name,
            result.result,
            result.reason,
            style=Style(color="green" if result.result == "pass" else "red"),
        )

    return table


async def handle_step_request(
    step_request: WebSocketStepRequestMessage,
    mcp_client: MCPStdioClient,
    ws_client: WebSocketClient,
) -> None:
    """Handle a step request from the WebSocket server."""
    console.print(step_request.message)
    result = await mcp_client.execute(step_request.tool)

    await ws_client.send(
        WebSocketStepResultMessage(
            job_id=step_request.job_id,
            tool=step_request.tool,
            status="success" if not result.isError else "error",
            output=str(result.content[0].model_dump()) if result.content else "",
        ).model_dump()
    )


def handle_complete_message(
    complete_message: WebSocketCompleteMessage, test_name: str
) -> NamedTestResult:
    """Handle a complete message from the WebSocket server."""
    if complete_message.result.result == "pass":
        console.print(f"[green]Test passed: {complete_message.result.reason}[/green]")
    else:
        console.print(f"[red]Test failed: {complete_message.result.reason}[/red]")

    return NamedTestResult(
        name=test_name,
        result=complete_message.result.result,
        reason=complete_message.result.reason,
    )


async def execute_test(test: Test, config: Config) -> NamedTestResult:
    """Execute a single test using WebSocket and MCP clients."""
    ws_client = WebSocketClient()
    mcp_client = MCPStdioClient()

    try:
        # Connect to WebSocket and initialize MCP
        await ws_client.connect()
        await mcp_client.init_client("npx", ["@playwright/mcp@latest", "--isolated"])

        # Send initial test data with config
        await ws_client.send(
            WebSocketInitTestMessage(
                test=test,
                config=config,
            ).model_dump()
        )

        # Main test loop
        while True:
            message = await ws_client.receive()

            if message["action"] == "step_request":
                step_request = WebSocketStepRequestMessage(**message)
                await handle_step_request(step_request, mcp_client, ws_client)

            elif message["action"] == "complete":
                complete_message = WebSocketCompleteMessage(**message)
                return handle_complete_message(complete_message, test.name)

    finally:
        await ws_client.close()
        await mcp_client.close()


async def test_command(test_path: Optional[str] = None):
    """Run Bugster tests."""
    try:
        # Load configuration and test files
        config = await load_config()
        path = Path(test_path) if test_path else None
        test_files = await load_test_files(path)

        if not test_files:
            console.print("[yellow]No test files found[/yellow]")
            return

        results = []

        # Execute each test
        for test_file in test_files:
            console.print(f"\n[blue]Running tests from {test_file['file']}[/blue]")

            for test_data in test_file["content"]:
                console.print(f"\n[green]Test: {test_data['name']}[/green]")
                test = Test(**test_data)
                results.append(await execute_test(test, config))

        # Display results table
        console.print(create_results_table(results))

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
