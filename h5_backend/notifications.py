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
