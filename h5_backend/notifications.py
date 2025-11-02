from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def notify_match_found(player1, player2):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"player_{player1.nickname}", {"type": "match.found", "opponent": player2.nickname, "points": player2.ranking_points}
    )
    async_to_sync(layer.group_send)(
        f"player_{player2.nickname}", {"type": "match.found", "opponent": player1.nickname, "points": player1.ranking_points}
    )


def notify_match_status_changed(player, opponent_accepted, opponent_declined):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"player_{player.nickname}",
        {
            "type": "check.if.accepted",
            "opponent_accepted": opponent_accepted,
            "opponent_declined": opponent_declined,
        },
    )


def notify_unaccepted_report(player, game):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"player_{player.nickname}",
        {
            "type": "unaccepted.report.data",
            "player1_nickname": game.player_1.nickname,
            "player2_nickname": game.player_2.nickname,
            "player1_castle": game.castle_1,
            "player2_castle": game.castle_2,
            "who_won": game.who_won.nickname,
        },
    )


def notify_opponent_left_queue(player, opponent):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"player_{player.nickname}",
        {
            "type": "opponent.left.queue",
            "opponent": opponent.nickname,
        },
    )


def notify_error(player, error):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"player_{player.nickname}",
        {
            "type": "error.occured",
            "error_message": error,
        },
    )
