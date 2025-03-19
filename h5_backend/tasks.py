import subprocess

from celery import shared_task
from django.db import transaction
from django.db.models import Q

from h5_backend.models import Player, PlayersMatched


@shared_task
def add_new_user_to_vpn_server(
    vpn_server_ip: str, vpn_admin_password: str, vpncmd_commands: str
) -> bool:
    vpncmd_path = "/usr/local/vpnserver/vpncmd"
    try:
        command = [
            vpncmd_path,
            vpn_server_ip,
            "/SERVER",
            f"/PASSWORD:{vpn_admin_password}",
            "/CMD",
        ]

        result = subprocess.run(
            command, input=vpncmd_commands, text=True, capture_output=True, check=True
        )

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
    players_in_queue = list(Player.objects.filter(player_state=Player.IN_QUEUE))
    # TODO: add enlarging mmr range dependant on time passed

    if len(players_in_queue) >= 2:
        player1 = players_in_queue[0]
        player2 = players_in_queue[1]

        with transaction.atomic():
            player1 = Player.objects.select_for_update().get(id=player1.id)
            player2 = Player.objects.select_for_update().get(id=player2.id)
            if not PlayersMatched.objects.filter(
                Q(player_1=player1, player_2=player2)
                | Q(player_1=player2, player_2=player1)
            ).exists():
                PlayersMatched.objects.create(
                    player_1=player1, player_2=player2, to_delete=False
                )

            player1.player_state = Player.WAITING_ACCEPTANCE
            player2.player_state = Player.WAITING_ACCEPTANCE
            player1.save()
            player2.save()


# @worker_ready.connect
# def start_message_server(sender, **kwargs):
#     server_thread = threading.Thread(target=Server().start, daemon=True)
#     server_thread.start()
