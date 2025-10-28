import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({"message": "Połączono z WebSocket!"}))

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(json.dumps({"echo": data}))
