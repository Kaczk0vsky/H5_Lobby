import json
import os
import logging

from datetime import timedelta

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth import authenticate
from django.db.models import Q
from django.db import transaction
from django.middleware.csrf import get_token
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.decorators import method_decorator
from django.urls import reverse

from h5_backend.tasks import add_new_user_to_vpn_server
from h5_backend.models import Player, PlayersMatched, Ban, Game
from h5_backend.serializers import UserSerializer

logger = logging.getLogger(__name__)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenView(View):
    def get(self, request, *args, **kwargs):
        token = get_token(request)
        return JsonResponse({"csrftoken": token})


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="3/m", method="POST", block=True), name="dispatch")
class RegisterPlayer(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            serializer = UserSerializer(data=data, required_fields=["nickname", "password", "email"])
            if not serializer.is_valid():
                return (None, None, None, JsonResponse({"success": False, "errors": serializer.errors}, status=400))

            nickname = serializer.validated_data["nickname"]
            password = serializer.validated_data["password"]
            email = serializer.validated_data["email"]

            return nickname, password, email, None

        except json.JSONDecodeError:
            return (None, None, None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400))

    def _validate_inputs(self, nickname, email):
        if User.objects.filter(username=nickname).exists():
            return JsonResponse({"success": False, "error": "Nickname already exists!"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "error": "Email already in use!"}, status=400)

    @staticmethod
    def _build_vpn_commands(nickname, password):
        return f"""
            Hub {os.getenv("VPN_HUB_NAME")}
            UserCreate {nickname} /GROUP:none /REALNAME:none /NOTE:none
            UserPasswordSet {nickname} /PASSWORD:{password}
        """

    def post(self, request, *args, **kwargs):
        try:
            nickname, password, email, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            error_response = self._validate_inputs(nickname, email)
            if error_response:
                return error_response

            vpncmd_commands = self._build_vpn_commands(nickname, password)

            with transaction.atomic():
                User.objects.create_user(username=nickname, password=password, email=email)
                add_new_user_to_vpn_server(
                    os.getenv("SERVER_URL"),
                    os.getenv("VPN_SERVER_PASSWORD"),
                    vpncmd_commands,
                )
                return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"Error registering new player: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong!"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="3/m", method="POST", block=True), name="dispatch")
class LoginPlayer(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            serializer = UserSerializer(data=data, required_fields=["nickname", "password"])
            if not serializer.is_valid():
                return (None, None, JsonResponse({"success": False, "errors": serializer.errors}, status=400))

            nickname = serializer.validated_data["nickname"]
            password = serializer.validated_data["password"]

            return nickname, password, None

        except json.JSONDecodeError:
            return (None, None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400))

    def _authenticate_user(self, nickname, password):
        user = authenticate(username=nickname, password=password)
        if user is None:
            return JsonResponse({"success": False, "error": "Invalid credentials"}, status=400)
        return None

    def _check_if_banned(self, player):
        ban = Ban.objects.filter(player=player).first()
        if ban:
            ban_duration = ban.get_time_left()
            if ban_duration == timedelta(0):
                ban.delete()
            else:
                return JsonResponse(
                    {"success": False, "error": f"You are banned for {ban_duration}"},
                    status=400,
                )

    def _update_player_state(self, player):
        player.player_state = "online"
        player.save()

    def post(self, request, *args, **kwargs):
        try:
            nickname, password, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            auth_error = self._authenticate_user(nickname, password)
            if auth_error:
                return auth_error

            try:
                player = Player.objects.get(nickname=nickname)
            except Player.DoesNotExist:
                return JsonResponse({"success": False, "error": "Player profile not found"}, status=400)

            ban_response = self._check_if_banned(player)
            if ban_response:
                return ban_response

            self._update_player_state(player)
            return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"Login error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="3/m", method="GET", block=True), name="dispatch")
class GeneratePasswordResetLinkView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            serializer = UserSerializer(data=request.GET, required_fields=["nickname", "email"])
            if not serializer.is_valid():
                return (None, None, JsonResponse({"success": False, "errors": serializer.errors}, status=400))

            nickname = serializer.validated_data["nickname"]
            email = serializer.validated_data["email"]

            return nickname, email, None

        except json.JSONDecodeError:
            return (None, None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400))

    def _generate_reset_link(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})

    def get(self, request, *args, **kwargs):
        try:
            nickname, email, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            try:
                user = User.objects.get(username=nickname, email=email)
            except User.DoesNotExist:
                return JsonResponse({"success": False, "error": "User not found"}, status=404)

            reset_url = self._generate_reset_link(user)
            return JsonResponse({"success": True, "reset_url": reset_url})

        except Exception as e:
            logger.error(f"Password reset link error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="5/m", method="POST", block=True), name="dispatch")
class SetPlayerStateView(View):
    state = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            serializer = UserSerializer(data=data, required_fields=["nickname"])
            if not serializer.is_valid():
                return None, JsonResponse({"success": False, "errors": serializer.errors}, status=400)

            nickname = serializer.validated_data["nickname"]

            return nickname, None

        except json.JSONDecodeError:
            return None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

    def _update_player_state(self, player):
        player.player_state = self.state
        player.save()

    def post(self, request, *args, **kwargs):
        try:
            if not self.state:
                return JsonResponse(
                    {"success": False, "error": "Invalid player state configuration"},
                    status=500,
                )

            nickname, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            try:
                player = Player.objects.get(nickname=nickname)
            except Player.DoesNotExist:
                return JsonResponse({"success": False, "error": "Player profile not found"}, status=400)

            self._update_player_state(player)
            return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"Setting player state error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="5/m", method="POST", block=True), name="dispatch")
class RemovePlayerFromQueue(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            serializer = UserSerializer(data=data, required_fields=["nickname", "is_accepted"])
            if not serializer.is_valid():
                return (None, None, JsonResponse({"success": False, "errors": serializer.errors}, status=400))

            nickname = serializer.validated_data["nickname"]
            queue_accepted = serializer.validated_data["is_accepted"]

            return nickname, queue_accepted, None

        except json.JSONDecodeError:
            return (None, None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400))

    def _update_player_state(self, player, player_state):
        player.player_state = player_state
        player.save()

    def _handle_queue_state(self, player):
        with transaction.atomic():
            try:
                player_matched = PlayersMatched.objects.get(Q(player_1=player) | Q(player_2=player))
                oponnent = player_matched.player_2 if player == player_matched.player_1 else player_matched.player_1
                oponnent.player_state = "in_queue"
                oponnent.save()
                player_matched.delete()

            except PlayersMatched.DoesNotExist:
                return JsonResponse({"success": False, "error": "Match not found"}, status=404)

    def post(self, request, *args, **kwargs):
        try:
            nickname, queue_accepted, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            player_state = "accepted" if queue_accepted else "online"

            try:
                player = Player.objects.get(nickname=nickname)
            except Player.DoesNotExist:
                return JsonResponse({"success": False, "error": "Player profile not found"}, status=400)

            self._update_player_state(player, player_state)
            if not queue_accepted:
                self._handle_queue_state(player)

            return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"Removing from queue error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="60/m", method="POST", block=True), name="dispatch")
class GetPlayersMatched(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            serializer = UserSerializer(data=data, required_fields=["nickname"])
            if not serializer.is_valid():
                return None, JsonResponse({"success": False, "errors": serializer.errors}, status=400)

            nickname = serializer.validated_data["nickname"]

            return nickname, None

        except json.JSONDecodeError:
            return None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

    def post(self, request, *args, **kwargs):
        try:
            nickname, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            try:
                player = Player.objects.get(nickname=nickname)
            except Player.DoesNotExist:
                return JsonResponse({"success": False, "error": "Player profile not found"}, status=400)

            try:
                player_matched = PlayersMatched.objects.filter(Q(player_1=player) | Q(player_2=player)).first()
            except PlayersMatched.DoesNotExist:
                return JsonResponse({"success": False, "game_found": False})

            opponent = player_matched.player_2 if player == player_matched.player_1 else player_matched.player_1
            return JsonResponse(
                {
                    "success": True,
                    "game_found": True,
                    "opponent": [opponent.nickname, opponent.ranking_points],
                }
            )

        except Exception as e:
            logger.error(f"Getting players matched error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="60/m", method="POST", block=True), name="dispatch")
class CheckIfOpponentAccepted(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            serializer = UserSerializer(data=data, required_fields=["nickname"])
            if not serializer.is_valid():
                return None, JsonResponse({"success": False, "errors": serializer.errors}, status=400)

            nickname = serializer.validated_data["nickname"]

            return nickname, None

        except json.JSONDecodeError:
            return None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

    def _handle_opponent_state(self, opponent, player, player_matched):
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

    def post(self, request, *args, **kwargs):
        try:
            nickname, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            try:
                player = Player.objects.get(nickname=nickname)
            except Player.DoesNotExist:
                return JsonResponse({"success": False, "error": "Player not found"}, status=400)
            try:
                player_matched = PlayersMatched.objects.get(Q(player_1=player) | Q(player_2=player))
            except PlayersMatched.DoesNotExist:
                return JsonResponse({"success": False, "error": "Player not found"}, status=400)

            opponent = player_matched.player_2 if player == player_matched.player_1 else player_matched.player_1
            response = self._handle_opponent_state(opponent, player, player_matched)
            return response

        except Exception as e:
            logger.error(f"Check if opponent accepted error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="10/m", method="POST", block=True), name="dispatch")
class UpdateUsersList(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            serializer = UserSerializer(data=data, required_fields=["nickname"])
            if not serializer.is_valid():
                return None, JsonResponse({"success": False, "errors": serializer.errors}, status=400)

            nickname = serializer.validated_data["nickname"]

            return nickname, None

        except json.JSONDecodeError:
            return None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

    def _get_online_players(self, nickname):
        try:
            players = Player.objects.exclude(player_state="offline").exclude(nickname=nickname)
            players_data = {
                nick: [ranking_points, player_state]
                for nick, ranking_points, player_state in players.values_list("nickname", "ranking_points", "player_state")
            }
            return players_data, None

        except Exception as e:
            return None, JsonResponse({"success": False, "error": "Players not found"}, status=400)

    def post(self, request, *args, **kwargs):
        try:
            nickname, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            players_data, fetch_error = self._get_online_players(nickname)
            if fetch_error:
                return fetch_error

            return JsonResponse({"success": True, "players_data": players_data})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)
        except Exception as e:
            logger.error(f"Checking if opponent accepted error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="3/m", method="POST", block=True), name="dispatch")
class HandleMatchReport:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            serializer = UserSerializer(data=data, required_fields=["nickname", "is_won"])
            if not serializer.is_valid():
                return None, None, JsonResponse({"success": False, "errors": serializer.errors}, status=400)

            nickname = serializer.validated_data["nickname"]
            game_won = serializer.validated_data["is_won"]

            return nickname, game_won, None

        except json.JSONDecodeError:
            return None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

    def _create_match_report(self, player, game_won):
        match = Game(player_1=player).save()

    def post(self, request, *args, **kwargs):
        try:
            nickname, game_won, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            try:
                player = Player.objects.get(nickname=nickname)
            except Player.DoesNotExist:
                return JsonResponse({"success": False, "error": "Players not found"}, status=400)

            self._create_match_report(player, game_won)

            return JsonResponse({"success": True, "created": True})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)
        except Exception as e:
            logger.error(f"Handling creating match report error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)
