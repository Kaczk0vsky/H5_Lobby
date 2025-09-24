import subprocess

from celery import shared_task
from django.db import transaction
from django.db.models import Q

from h5_backend.models import Player, Game, PlayerState


@shared_task
def add_new_user_to_vpn_server(vpn_server_ip: str, vpn_admin_password: str, vpncmd_commands: str) -> bool:
    vpncmd_path = "/usr/local/vpnserver/vpncmd"
    try:
        command = [
            vpncmd_path,
            vpn_server_ip,
            "/SERVER",
            f"/PASSWORD:{vpn_admin_password}",
            "/CMD",
        ]

        result = subprocess.run(command, input=vpncmd_commands, text=True, capture_output=True, check=True)

        if result.returncode != 0:
            print("Error Output:", result.stderr)
            return False

        return True

    except subprocess.CalledProcessError as e:
        print("Subprocess Error:", e.stderr)
        return False
    except Exception as e:
        print("General Error:", str(e))
        return False


@shared_task
def check_queue():
    queues = [
        {"players": list(Player.objects.filter(player_state=PlayerState.IN_QUEUE, is_searching_ranked=True)), "is_ranked": True},
        {"players": list(Player.objects.filter(player_state=PlayerState.IN_QUEUE, is_searching_ranked=False)), "is_ranked": False},
    ]

    for queue in queues:
        players = queue["players"]
        is_ranked = queue["is_ranked"]

        if len(players) < 2:
            continue

        for player1 in players:
            for player2 in players:
                if player1 == player2:
                    continue

                if (player1.ranking_points > player2.min_opponent_points and player2.ranking_points > player1.min_opponent_points) or not is_ranked:
                    with transaction.atomic():
                        player1_locked = Player.objects.select_for_update().get(id=player1.id)
                        player2_locked = Player.objects.select_for_update().get(id=player2.id)

                        existing_game = Game.objects.filter(
                            Q(player_1=player1_locked, player_2=player2_locked, is_new=True)
                            | Q(player_1=player2_locked, player_2=player1_locked, is_new=True)
                        )

                        if not existing_game.exists():
                            Game.objects.create(player_1=player1_locked, player_2=player2_locked, is_new=True, is_ranked=is_ranked)

                            player1_locked.player_state = PlayerState.WAITING_ACCEPTANCE
                            player2_locked.player_state = PlayerState.WAITING_ACCEPTANCE
                            player1_locked.save()
                            player2_locked.save()
