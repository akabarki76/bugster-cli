"""
WebSocket client implementation using websockets library
"""

import json
import ssl
from typing import Dict, Any, Optional
import websockets
from websockets.asyncio.client import ClientConnection


class WebSocketClient:
    def __init__(self):
        """Initialize WebSocket client"""
        self.ws: Optional[ClientConnection] = None
        # self.url = "wss://5jkw97w149.execute-api.us-east-1.amazonaws.com/dev"
        self.url = "ws://localhost:8765"
        self.connected = False

        # Create SSL context that ignores certificate verification
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def connect(self):
        """Connect to WebSocket server"""
        if self.url.startswith("wss"):
            self.ws = await websockets.connect(self.url, ssl=self.ssl_context)
        else:
            self.ws = await websockets.connect(self.url)
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


if __name__ == "__main__":
    import asyncio

    async def main():
        client = WebSocketClient()
        await client.connect()
        await client.send({"action": "test", "description": "Hello, world!"})
        print(await client.receive())
        await client.close()

    asyncio.run(main())
