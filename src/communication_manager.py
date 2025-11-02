import asyncio
import json
import websockets

from src.global_vars import env_dict
from utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketClient:
    def __init__(self, user):
        self.user = user
        self.ws = None
        self._found_game = False
        self._update_queue_status = False
        self._opponent_nickname = None
        self._opponent_ranking_points = None
        self._opponent_accepted = False
        self._opponent_declined = False
        self._message_queue = asyncio.Queue()

    async def connect(self):
        uri = f"wss://{env_dict['SERVER_URL']}/ws/queue/{self.user['nickname']}/"
        self.ws = await websockets.connect(uri)
        asyncio.create_task(self.listen())
        logger.info("Connected to WebSocket.")

    async def disconnect(self):
        if self.ws and not self.ws.closed:
            await self.ws.close()
            logger.info("WebSocket connection closed.")

    async def listen(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self._message_queue.put(data)
        except websockets.ConnectionClosed:
            logger.warning("WebSocket connection closed. Attempting to reconnect...")
            await self.reconnect()
        except Exception as e:
            logger.error(f"Unexpected error in listen(): {e}")

    async def reconnect(self):
        self.ws = None
        await asyncio.sleep(3)
        await self.connect()

    async def send(self, payload):
        if self.ws:
            await self.ws.send(json.dumps(payload))
            logger.debug(f"Sent: {payload["action"]}")
        else:
            logger.warning("Tried to send message, but WebSocket is closed.")
