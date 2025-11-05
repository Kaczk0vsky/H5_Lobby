from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from h5_backend.models import OfflineMessage, Player, PlayerState


def send_or_store(player: Player, event_type: str, payload: dict):
    layer = get_channel_layer()
    group_name = f"player_{player.nickname}"
    if player.player_state != PlayerState.OFFLINE and player.connected_to_ws:
        async_to_sync(layer.group_send)(group_name, {"type": event_type, **payload})
    else:
        OfflineMessage.objects.create(recipient=player, event_type=event_type, payload=payload)


def notify_match_found(player1, player2, is_invited):
    send_or_store(player1, "match_found", {"opponent": player2.nickname, "points": player2.ranking_points, "is_invited": is_invited})
    send_or_store(player2, "match_found", {"opponent": player1.nickname, "points": player1.ranking_points, "is_invited": is_invited})


def notify_match_status_changed(player, opponent_accepted, opponent_declined):
    send_or_store(player, "check_if_accepted", {"opponent_accepted": opponent_accepted, "opponent_declined": opponent_declined})


def notify_unaccepted_report(player, game):
    send_or_store(
        player,
        "unaccepted_report_data",
        {
            "player1_nickname": game.player_1.nickname,
            "player2_nickname": game.player_2.nickname,
            "player1_castle": game.castle_1,
            "player2_castle": game.castle_2,
            "who_won": game.who_won.nickname,
        },
    )


def notify_opponent_left_queue(player, opponent):
    send_or_store(player, "opponent_left_queue", {"opponent": opponent.nickname})


def notify_users_list_change(player, users_list):
    send_or_store(player, "refresh_friend_list", {"users_list": users_list})
