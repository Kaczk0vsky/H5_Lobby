import json
import os
import logging
import re

from dotenv import load_dotenv
from datetime import timedelta

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth import authenticate
from django.db.models import Q
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

from h5_backend.tasks import add_new_user_to_vpn_server
from h5_backend.models import Player, PlayersMatched, Ban

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({"csrftoken": token})


@csrf_protect
@require_POST
@ratelimit(key="user_or_ip", rate="3/m", method="POST", block=True)
def register_new_player(request):
    load_dotenv()
    try:
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        password = data.get("password")
        email = data.get("email")

        if not (nickname and password and email):
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", nickname):
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            return JsonResponse(
                {"success": False, "error": "Invalid email format"}, status=400
            )

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#$%^&+=!]{8,}$", password):
            return JsonResponse(
                {"success": False, "error": "Invalid password"}, status=400
            )

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse(
                {"success": False, "error": "Invalid email format"}, status=400
            )

        if User.objects.filter(username=nickname).exists():
            return JsonResponse(
                {"success": False, "error": "Nickname already exists!"}, status=400
            )

        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"success": False, "error": "Email already in use!"}, status=400
            )

        vpn_server_ip = os.getenv("SERVER_URL")
        vpn_server_password = os.getenv("VPN_SERVER_PASSWORD")
        vpn_hub = os.getenv("VPN_HUB_NAME")
        vpncmd_commands = f"""
            Hub {vpn_hub}
            UserCreate {nickname} /GROUP:none /REALNAME:none /NOTE:none
            UserPasswordSet {nickname} /PASSWORD:{password}
        """

        with transaction.atomic():
            User.objects.create_user(username=nickname, password=password, email=email)
            add_new_user_to_vpn_server(
                vpn_server_ip, vpn_server_password, vpncmd_commands
            )
            return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON format"}, status=400
        )

    except Exception as e:
        logger.error(f"Error registering new player: {e}")
        return JsonResponse(
            {"success": False, "error": "Something went wrong!"}, status=500
        )


@csrf_protect
@require_POST
@ratelimit(key="user_or_ip", rate="3/m", method="POST", block=True)
def login_player(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        password = data.get("password")

        if not (nickname and password):
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        if not nickname.isalnum():
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", nickname):
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#$%^&+=!]{8,}$", password):
            return JsonResponse(
                {"success": False, "error": "Invalid password"}, status=400
            )

        user = authenticate(username=nickname, password=password)
        if user is None:
            return JsonResponse(
                {"success": False, "error": "Invalid credentials"}, status=400
            )

        try:
            player = Player.objects.get(nickname=nickname)
            if Ban.objects.filter(player=player).exists():
                ban = Ban.objects.filter(player=player).get()
                ban_duration = ban.get_time_left()
                if ban_duration == timedelta(0):
                    ban.delete()
                else:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": f"You are banned for {ban_duration}",
                        },
                        status=400,
                    )
            player.player_state = "online"
            player.save()
        except Player.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Player profile not found"}, status=400
            )
        return JsonResponse({"success": True})
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON format"}, status=400
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JsonResponse(
            {"success": False, "error": "Something went wrong"}, status=500
        )


@csrf_protect
@require_GET
@ratelimit(key="user_or_ip", rate="3/m", method="GET", block=True)
def change_password(request):
    try:
        nickname = request.GET.get("nickname")
        email = request.GET.get("email")
        if not (nickname and email):
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", nickname):
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            return JsonResponse(
                {"success": False, "error": "Invalid email format"}, status=400
            )

        try:
            user = User.objects.get(username=nickname, email=email)
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = reverse(
                    "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
                )
                return JsonResponse({"success": True, "reset_url": reset_url})
            else:
                return JsonResponse(
                    {"success": False, "error": "Invalid credentials"}, status=400
                )
        except User.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "User not found"}, status=404
            )
    except Exception as e:
        logger.error(f"Changing password error: {e}")
        return JsonResponse(
            {"success": False, "error": "Something went wrong"}, status=500
        )


@csrf_protect
@require_POST
@ratelimit(key="user_or_ip", rate="5/m", method="POST", block=True)
def set_player_offline(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")

        if not nickname:
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        if not nickname.isalnum():
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", nickname):
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        try:
            player = Player.objects.get(nickname=nickname)
            player.player_state = "offline"
            player.save()
            return JsonResponse({"success": True})

        except Player.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Player profile not found"}, status=400
            )
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON format"}, status=400
        )
    except Exception as e:
        logger.error(f"Setting player offline error: {e}")
        return JsonResponse(
            {"success": False, "error": "Something went wrong"}, status=500
        )


@csrf_protect
@require_POST
@ratelimit(key="user_or_ip", rate="3/m", method="POST", block=True)
def add_to_queue(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")

        if not nickname:
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        if not nickname.isalnum():
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", nickname):
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        try:
            player = Player.objects.get(nickname=nickname)
            player.player_state = "in_queue"
            player.save()
            return JsonResponse({"success": True})

        except Player.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Player profile not found"}, status=400
            )
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON format"}, status=400
        )
    except Exception as e:
        logger.error(f"Adding to queue error: {e}")
        return JsonResponse(
            {"success": False, "error": "Something went wrong"}, status=500
        )


@csrf_protect
@require_POST
@ratelimit(key="user_or_ip", rate="3/m", method="POST", block=True)
def remove_from_queue(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")
        is_accepted = data.get("is_accepted")
        player_state = "accepted" if is_accepted else "online"

        if not nickname:
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        if not nickname.isalnum():
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", nickname):
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        try:
            player = Player.objects.get(nickname=nickname)
            player.player_state = player_state
            player.save()

        except Player.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Player profile not found"}, status=400
            )

        if not is_accepted:
            with transaction.atomic():
                try:
                    player_matched = PlayersMatched.objects.get(
                        Q(player_1=player) | Q(player_2=player)
                    )
                    oponnent = (
                        player_matched.player_2
                        if player == player_matched.player_1
                        else player_matched.player_1
                    )
                    oponnent.player_state = "in_queue"
                    oponnent.save()
                    player_matched.delete()

                except PlayersMatched.DoesNotExist:
                    return JsonResponse(
                        {"success": False, "error": "Match not found"}, status=404
                    )
        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON format"}, status=400
        )
    except Exception as e:
        logger.error(f"Removing from queue error: {e}")
        return JsonResponse(
            {"success": False, "error": "Something went wrong"}, status=500
        )


@csrf_protect
@require_POST
@ratelimit(key="user_or_ip", rate="60/m", method="POST", block=True)
def get_players_matched(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")

        if not nickname:
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        if not nickname.isalnum():
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", nickname):
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        player = Player.objects.filter(nickname=nickname).first()
        if not player:
            return JsonResponse(
                {"success": False, "error": "Player not found"}, status=404
            )

        player_matched = PlayersMatched.objects.filter(
            Q(player_1=player) | Q(player_2=player)
        ).first()

        if not player_matched:
            return JsonResponse({"success": False, "game_found": False})

        opponent = (
            player_matched.player_2
            if player == player_matched.player_1
            else player_matched.player_1
        )

        return JsonResponse(
            {
                "success": True,
                "game_found": True,
                "opponent": [opponent.nickname, opponent.ranking_points],
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON format"}, status=400
        )
    except Exception as e:
        logger.error(f"Getting players matched error: {e}")
        return JsonResponse(
            {"success": False, "error": "Something went wrong"}, status=500
        )


@csrf_protect
@require_POST
@ratelimit(key="user_or_ip", rate="60/m", method="POST", block=True)
def check_if_oponnent_accepted(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        nickname = data.get("nickname")

        if not nickname:
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        if not nickname.isalnum():
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", nickname):
            return JsonResponse(
                {"success": False, "error": "Invalid nickname format"}, status=400
            )

        try:
            player = Player.objects.get(nickname=nickname)
        except Player.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Player not found"}, status=400
            )
        try:
            player_matched = PlayersMatched.objects.get(
                Q(player_1=player) | Q(player_2=player)
            )
        except PlayersMatched.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Player not found"}, status=400
            )

        opponent = (
            player_matched.player_2
            if player == player_matched.player_1
            else player_matched.player_1
        )

        if opponent.player_state == "accepted" or opponent.player_state == "playing":
            opponent.player_state = "playing"
            player.player_state = "playing"

            with transaction.atomic():
                opponent.save()
                player.save()

                if player_matched.to_delete:
                    player_matched.delete()
                else:
                    player_matched.to_delete = True
                    player_matched.save()

                return JsonResponse(
                    {
                        "success": True,
                        "oponnent_accepted": True,
                        "oponnent_declined": False,
                    }
                )

        elif opponent.player_state == "online" or opponent.player_state == "offline":
            with transaction.atomic():
                player_matched.delete()
                player.player_state = "in_queue"
                player.save()

                return JsonResponse(
                    {
                        "success": True,
                        "oponnent_accepted": False,
                        "oponnent_declined": True,
                    }
                )

        return JsonResponse({"success": True, "oponnent_accepted": False})

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON format"}, status=400
        )
    except Exception as e:
        logger.error(f"Checking if opponent accepted error: {e}")
        return JsonResponse(
            {"success": False, "error": "Something went wrong"}, status=500
        )
