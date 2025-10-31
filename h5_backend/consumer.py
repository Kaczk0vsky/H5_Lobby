import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction
from django.db.models import Q
from asgiref.sync import sync_to_async

from h5_backend.models import Player, Game, Ban, PlayerState
from h5_backend.notifications import notify_match_status_changed


class ModelParser:
    async def _get_player(self, nickname):
        @sync_to_async
        def get_player():
            try:
                return Player.objects.get(nickname=nickname)
            except Player.DoesNotExist:
                return None

        return await get_player()

    async def _get_game(self, player):
        @sync_to_async
        def get_game():
            try:
                return Game.objects.filter(Q(player_1=player, is_new=True) | Q(player_2=player, is_new=True)).get()
            except Game.DoesNotExist:
                return None

        return await get_game()

    async def _get_ban(self, player):
        @sync_to_async
        def get_ban():
            try:
                return Ban.objects.get(player=player)
            except Ban.DoesNotExist:
                return None

        return await get_ban()


class QueueConsumer(AsyncWebsocketConsumer, ModelParser):
    async def connect(self):
        self.nickname = self.scope["url_route"]["kwargs"]["nickname"]
        self.group_name = f"player_{self.nickname}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "check_if_accepted":
            await self._check_if_accepted(data)
        else:
            pass

    async def _check_if_accepted(self, data):
        nickname = data.get("nickname")
        player = await self._get_player(nickname)
        game = await self._get_game(player)

        @sync_to_async
        def update_state():
            opponent = game.player_2 if player == game.player_1 else game.player_1

            if opponent.player_state in [PlayerState.ACCEPTED, PlayerState.PLAYING]:
                with transaction.atomic():
                    opponent.player_state = PlayerState.PLAYING
                    player.player_state = PlayerState.PLAYING
                    opponent.save()
                    player.save()
                notify_match_status_changed(player, True, False)
                notify_match_status_changed(opponent, True, False)
            elif opponent.player_state in [PlayerState.ONLINE, PlayerState.OFFLINE]:
                with transaction.atomic():
                    game.delete()
                    player.player_state = PlayerState.IN_QUEUE
                    player.save()
                notify_match_status_changed(player, False, True)
                # notify_match_status_changed(opponent, True, False)

        await update_state()

    # EVENT HANDLERS
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

    async def check_if_accepted(self, event):
        await self.send(
            json.dumps(
                {
                    "event": "match_status_changed",
                    "opponent_accepted": event["opponent_accepted"],
                    "opponent_declined": event["opponent_declined"],
                }
            )
        )
