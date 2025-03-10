from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.http import HttpResponse

from h5_backend.settings_handler import load_server_settings
from h5_backend.tasks import add_new_user_to_vpn_server
from h5_backend.models import Player

from dotenv import load_dotenv

import json
import os


@csrf_exempt  # Disable CSRF for external requests; for production, secure this with proper auth
def register_new_player(request):
    load_dotenv()
    server_settings = load_server_settings()
    data = {"last_available_ip": server_settings["last_available_ip"]}

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
