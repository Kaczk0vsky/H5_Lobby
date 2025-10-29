import json

from channels.generic.websocket import AsyncWebsocketConsumer


class QueueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.nickname = self.scope["url_route"]["kwargs"]["nickname"]
        self.group_name = f"player_{self.nickname}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def match_found(self, event):
        await self.send(
            json.dumps(
                {
                    "event": "match_found",
                    "opponent": event["opponent"],
                    "points": event["points"],
                }
            )
        )
