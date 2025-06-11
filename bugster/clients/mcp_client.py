"""
MCP Stdio Client
"""

from typing import Dict, Any, List, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, ListToolsResult, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult

from bugster.types import ToolRequest


class MCPStdioClient:
    def __init__(self):
        """Initialize MCP client"""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None

    async def init_client(
        self, command: str, args: List[str], env: Optional[Dict[str, str]] = None
    ):
        """Initialize MCP client and session"""
        if not self.session:
            server_params = StdioServerParameters(command=command, args=args, env=env)

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            await self.session.initialize()

    async def list_tools(self) -> ListToolsResult:
        """List available tools"""
        response = await self.session.list_tools()
        return response.tools

    async def execute(self, tool: ToolRequest) -> CallToolResult:
        """Execute a tool using MCP"""
        result = await self.session.call_tool(tool.name, tool.args)
        return result

    async def close(self):
        """Close MCP client"""
        if self.session:
            await self.exit_stack.aclose()
