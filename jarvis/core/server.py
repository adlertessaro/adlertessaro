import asyncio
import json
import logging
import threading
import webbrowser
from pathlib import Path

import websockets

logger = logging.getLogger("jarvis.server")

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


class WebSocketServer:
    """Bridges the Python backend to the browser frontend via WebSocket."""

    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self._loop = None
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self):
        async with websockets.serve(self._handler, self.host, self.port):
            logger.info(f"WebSocket server on ws://{self.host}:{self.port}")
            await asyncio.Future()

    async def _handler(self, websocket):
        self.clients.add(websocket)
        logger.info(f"Client connected ({len(self.clients)} total)")
        try:
            async for message in websocket:
                pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            logger.info(f"Client disconnected ({len(self.clients)} total)")

    def broadcast(self, event_type: str, data: dict = None):
        if not self._loop or not self.clients:
            return
        message = json.dumps({"type": event_type, **(data or {})})
        asyncio.run_coroutine_threadsafe(self._broadcast(message), self._loop)

    async def _broadcast(self, message: str):
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True,
            )

    def open_frontend(self):
        url = f"file://{FRONTEND_DIR / 'index.html'}"
        webbrowser.open(url)
