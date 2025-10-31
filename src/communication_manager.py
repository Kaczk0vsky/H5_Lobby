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

    async def connect(self):
        uri = f"wss://{env_dict['SERVER_URL']}/ws/queue/{self.user['nickname']}/"
        logger.info(f"Connecting to WebSocket - User: {self.user['nickname']}")
        self.ws = await websockets.connect(uri)
        asyncio.create_task(self.listen())

    async def disconnect(self):
        if self.ws and not self.ws.closed:
            await self.ws.close()
            logger.info("WebSocket connection closed.")

    async def listen(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.ConnectionClosed:
            logger.warning("WebSocket connection closed. Attempting to reconnect...")
            await self.reconnect()
        except Exception as e:
            logger.error(f"Unexpected error in listen(): {e}")

    async def reconnect(self):
        await asyncio.sleep(3)
        await self.connect()

    async def send(self, payload):
        if self.ws and not self.ws.closed:
            await self.ws.send(json.dumps(payload))
        else:
            logger.warning("Tried to send message, but WebSocket is closed.")

    async def handle_message(self, data):
        event = data.get("event")
        logger.debug(f"Handling message: {data}")

        if event == "add_to_queue":
            pass

        elif event == "remove_from_queue":
            pass

        elif event == "match_found":
            self._update_queue_status = True
            self._found_game = True
            self._opponent_nickname = data["opponent"]
            self._opponent_ranking_points = data["points"]
            logger.debug(f"Found opponent: {self._opponent_nickname}")

        elif event == "match_status_changed":
            self._opponent_accepted = data["opponent_accepted"]
            self._opponent_declined = data["opponent_declined"]

            if not self._opponent_accepted and not self._opponent_declined:
                logger.debug("Opponent is still deciding.")
            else:
                logger.debug("Got opponent acceptance status.")

        elif event == "refresh_friend_list":
            pass

        else:
            logger.warning(f"Unknown event type: {event}")
