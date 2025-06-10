"""
WebSocket client implementation using websockets library
"""

import json
import ssl
from typing import Dict, Any, Optional
import websockets
from websockets.asyncio.client import ClientConnection
from bugster.utils.user_config import get_api_key, get_org_id, get_user_id


class WebSocketClient:
    def __init__(self):
        """Initialize WebSocket client"""
        self.ws: Optional[ClientConnection] = None
        self.base_url = "wss://websocket.bugster.app/prod/"
        # self.base_url = "ws://localhost:8765"
        self.connected = False

        # Create SSL context that ignores certificate verification
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def connect(self):
        """Connect to WebSocket server"""
        # Get API key from config
        api_key = get_api_key()
        if not api_key:
            raise RuntimeError(
                "API key not found. Please run 'bugster login' to set up your API key."
            )

        # Get org_id and user_id from config
        org_id = get_org_id()
        user_id = get_user_id()

        # Build URL with query parameters
        url = f"{self.base_url}?org_id={org_id}&user_id={user_id}"

        # Add API key to headers
        additional_headers = {"X-API-Key": api_key}

        if url.startswith("wss"):
            self.ws = await websockets.connect(
                url,
                ssl=self.ssl_context,
                open_timeout=30,
                additional_headers=additional_headers,
            )
        else:
            self.ws = await websockets.connect(
                url,
                open_timeout=30,
                additional_headers=additional_headers,
            )
        self.connected = True

    async def close(self):
        """Close WebSocket connection"""
        if self.ws:
            await self.ws.close()
            self.connected = False
            self.ws = None

    async def send(self, data: Dict[str, Any]):
        """Send data to WebSocket server"""
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
        await self.ws.send(json.dumps(data))

    async def receive(self) -> Dict[str, Any]:
        """Receive data from WebSocket server"""
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
        message = await self.ws.recv()
        return json.loads(message)
