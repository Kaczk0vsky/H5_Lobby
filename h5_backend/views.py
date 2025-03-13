import json
import os

from dotenv import load_dotenv

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.db.models import Q

from h5_backend.tasks import add_new_user_to_vpn_server
from h5_backend.models import Player, PlayersMatched


@csrf_exempt  # Disable CSRF for external requests; for production, secure this with proper auth
def register_new_player(request):
    load_dotenv()

    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        password = data.get("password")
        email = data.get("email")
        vpn_server_ip = os.getenv("SERVER_URL")
        vpn_server_password = os.getenv("VPN_SERVER_PASSWORD")
        vpn_hub = os.getenv("VPN_HUB_NAME")

        try:
            user = User.objects.create_user(
                username=nickname, password=password, email=email
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

        vpncmd_commands = f"""
            Hub {vpn_hub}
            UserCreate {nickname} /GROUP:none /REALNAME:none /NOTE:none
            UserPasswordSet {nickname} /PASSWORD:{password}
        """
        result = add_new_user_to_vpn_server(
            vpn_server_ip, vpn_server_password, vpncmd_commands
        )

        if not result:
            return JsonResponse(
                {"success": False, "error": "Something went wrong!"}, status=500
            )
        return JsonResponse({"success": True, "user_id": user.id})
    elif request.method == "GET":
        return JsonResponse(data)

    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


@csrf_exempt  # Disable CSRF for external requests; for production, secure this with proper auth
def login_player(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        password = data.get("password")
        try:
            user = authenticate(username=nickname, password=password)
            if user is not None:
                player = Player.objects.get(nickname=nickname)
                player.player_state = "online"
                player.save()
                return JsonResponse({"success": True, "user_id": user.id})
            else:
                return JsonResponse(
                    {"success": False, "error": "Invalid credentials"}, status=400
                )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


@csrf_exempt
def set_player_offline(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        try:
            player = Player.objects.get(nickname=nickname)
            player.player_state = "offline"
            player.save()
            if player is not None:
                return JsonResponse({"success": True, "user_id": player.id})
            else:
                return JsonResponse(
                    {"success": False, "error": "Invalid credentials"}, status=400
                )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


@csrf_exempt
def add_to_queue(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        try:
            player = Player.objects.get(nickname=nickname)
            player.player_state = "in_queue"
            player.save()

            return JsonResponse({"success": True})
        except:
            return JsonResponse(
                {"success": False, "error": "Invalid credentials"}, status=400
            )
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


@csrf_exempt
def remove_from_queue(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        is_playing = data.get("is_playing")
        player_state = "playing" if is_playing else "online"
        try:
            player = Player.objects.get(nickname=nickname)
            player.player_state = player_state
            player.save()

            PlayersMatched.objects.filter(
                Q(player_1=player) | Q(player_2=player)
            ).delete()

            return JsonResponse({"success": True})
        except:
            return JsonResponse(
                {"success": False, "error": "Invalid credentials"}, status=400
            )
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


@csrf_exempt
def get_players_matched(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            nickname = data.get("nickname")
            players_in_queue = Player.objects.filter(player_state=Player.IN_QUEUE)

            if players_in_queue.count() < 2:
                return JsonResponse({"success": True, "game_found": False})

            players_1_list = list(
                PlayersMatched.objects.values_list("player_1_matched", flat=True)
            )
            players_2_list = list(
                PlayersMatched.objects.values_list("player_2_matched", flat=True)
            )
            players_list = players_1_list + players_2_list

            return JsonResponse(
                {"success": True, "game_found": nickname in players_list}
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "Invalid JSON format"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


def ashanarena(request):
    return HttpResponse(
        "Greetings, Noble Warrior! Behold, the AshanArena3 is currently under construction. Take heed and return in the future, for great wonders shall await thee... Thou shalt not be disappointed!"
    )
