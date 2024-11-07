from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.http import HttpResponse

from h5_backend.settings_handler import load_server_settings, save_server_settings

import json
import subprocess


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
            f"AllowedIPs = {server_settings["last_available_ip"]}",
        ]

        if password != repeat_password or "@" not in email:
            return JsonResponse(
                {"success": False, "error": "Invalid input"}, status=400
            )

        try:
            user = User.objects.create_user(
                username=nickname, password=password, email=email
            )
            with open(conf_path, "a") as file:
                file.write("\n".join(conf_content))
            try:
                subprocess.run(
                    ["sudo", "systemctl", "restart", "wg-quick@H5_Server"], check=True
                )
                print("WireGuard service restarted successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to restart WireGuard service: {e}")
            save_server_settings()
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
            return JsonResponse({"success": True, "user_id": user.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


def ashanarena(request):
    return HttpResponse(
        "Greetings, Noble Warrior! Behold, the AshanArena3 is currently under construction. Take heed and return in the future, for great wonders shall await thee... Thou shalt not be disappointed!"
    )
