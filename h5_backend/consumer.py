import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction
from django.db.models import Q
from asgiref.sync import sync_to_async

from h5_backend.models import Player, Game, Ban, PlayerState
from h5_backend.notifications import notify_match_status_changed, notify_unaccepted_report, notify_opponent_left_queue, notify_error


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

    async def _get_unaccepted_game(self, player):
        @sync_to_async
        def get_unaccepted_game():
            try:
                return (
                    Game.objects.filter(Q(player_1=player) | Q(player_2=player), is_waiting_confirmation=True)
                    .exclude(who_created=player)
                    .order_by("-id")
                    .last()
                )
            except Game.DoesNotExist:
                return None

        return await get_unaccepted_game()

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
        try:
            data = json.loads(text_data)
            action = data.get("action")
            if action == "add_to_queue":
                await self._add_to_queue(data)
            elif action == "remove_from_queue":
                await self._remove_from_queue(data)
            elif action == "check_if_accepted":
                await self._check_if_accepted(data)
            else:
                pass
        except Exception as e:
            pass

    async def _add_to_queue(self, data):
        nickname = data.get("nickname")
        is_searching_ranked = data.get("is_searching_ranked")
        min_opponent_points = data.get("min_opponent_points")
        player = await self._get_player(nickname)
        if not player:
            raise ValueError(f"Player {nickname} not found")

        # unaccepted_game = await self._get_unaccepted_game(player)
        # if unaccepted_game:
        #     notify_unaccepted_report(player, unaccepted_game)
        #     raise ValueError(f"You have unconfirmed report!")

        @sync_to_async
        def add_to_queue():
            with transaction.atomic():
                player.player_state = PlayerState.IN_QUEUE
                player.is_searching_ranked = is_searching_ranked
                player.min_opponent_points = min_opponent_points
                player.save()

        await add_to_queue()

    async def _remove_from_queue(self, data):
        nickname = data.get("nickname")
        is_queue_accepted = data.get("is_accepted")
        player = await self._get_player(nickname)
        if not player:
            raise ValueError(f"Player {nickname} not found")

        game = await self._get_game(player)

        @sync_to_async
        def remove_from_queue():
            with transaction.atomic():
                player.player_state = PlayerState.ACCEPTED if is_queue_accepted else PlayerState.ONLINE
                player.save()
                if not is_queue_accepted and game:
                    opponent = game.player_2 if player == game.player_1 else game.player_1
                    opponent.player_state = PlayerState.IN_QUEUE
                    opponent.save()
                    game.delete()
                    notify_opponent_left_queue(opponent, player)

        await remove_from_queue()

    async def _check_if_accepted(self, data):
        nickname = data.get("nickname")
        player = await self._get_player(nickname)
        if not player:
            raise ValueError(f"Player {nickname} not found")

        game = await self._get_game(player)
        if not game:
            raise ValueError(f"Game not found for player: {nickname}")

        @sync_to_async
        def update_state():
            with transaction.atomic():
                player.player_state = PlayerState.ACCEPTED
                player.save()
            opponent = game.player_2 if player == game.player_1 else game.player_1

            if opponent.player_state == PlayerState.ACCEPTED:
                with transaction.atomic():
                    opponent.player_state = PlayerState.PLAYING
                    player.player_state = PlayerState.PLAYING
                    opponent.save()
                    player.save()
                notify_match_status_changed(player, True, False)
                notify_match_status_changed(opponent, True, False)
            elif opponent.player_state == PlayerState.WAITING_ACCEPTANCE:
                notify_match_status_changed(player, False, False)
            elif opponent.player_state in [PlayerState.ONLINE, PlayerState.OFFLINE]:
                with transaction.atomic():
                    game.delete()
                    player.player_state = PlayerState.IN_QUEUE
                    player.save()
                notify_match_status_changed(player, False, True)

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

    async def match_status_changed(self, event):
        await self.send(
            json.dumps(
                {
                    "event": "match_status_changed",
                    "opponent_accepted": event["opponent_accepted"],
                    "opponent_declined": event["opponent_declined"],
                }
            )
        )

    async def unaccepted_report_data(self, event):
        await self.send(
            json.dumps(
                {
                    "event": "unaccepted_report_data",
                    event["player1_nickname"]: event["player1_castle"],
                    event["player2_nickname"]: event["player2_castle"],
                    "who_won": event.game.who_won.nickname,
                }
            )
        )

    async def opponent_left_queue(self, event):
        await self.send(
            json.dumps(
                {
                    "event": "opponent_left_queue",
                    "opponent": event["opponent"],
                }
            )
        )

    async def error_occured(self, event):
        await self.send(
            json.dumps(
                {
                    "event": "error_occured",
                    "error_message": event["error_message"],
                }
            )
        )
