from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.http import HttpResponse

from h5_backend.settings_handler import load_server_settings
from h5_backend.tasks import update_wireguard_config
from h5_backend.models import Player

import json


@csrf_exempt  # Disable CSRF for external requests; for production, secure this with proper auth
def register_new_player(request):
    server_settings = load_server_settings()
    data = {"last_available_ip": server_settings["last_available_ip"]}

    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        password = data.get("password")
        repeat_password = data.get("repeat_password")
        email = data.get("email")
        client_private_key = data.get("client_private_key")
        client_public_key = data.get("client_public_key")
        conf_path = "/etc/wireguard/H5_Server.conf"
        conf_content = [
            "\n",
            "[Peer]",
            f"PublicKey = {client_public_key}",
            f"AllowedIPs = {server_settings["last_available_ip"]}/32",
        ]

        if password != repeat_password or "@" not in email:
            return JsonResponse(
                {"success": False, "error": "Invalid input"}, status=400
            )

        try:
            user = User.objects.create_user(
                username=nickname, password=password, email=email
            )
            update_wireguard_config(conf_path, conf_content)
            return JsonResponse({"success": True, "user_id": user.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

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
                player.player_state = Player.ONLINE
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
            player.player_state = Player.OFFLINE
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


def ashanarena(request):
    return HttpResponse(
        "Greetings, Noble Warrior! Behold, the AshanArena3 is currently under construction. Take heed and return in the future, for great wonders shall await thee... Thou shalt not be disappointed!"
    )
