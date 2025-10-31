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
from h5_backend.models import Player, PlayerState, Ban, Game, CastleType
from h5_backend.serializers import UserSerializer, GameReportSerializer

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

            request_data = {}
            request_data["nickname"] = serializer.validated_data["nickname"]
            if self.state == "in_queue":
                request_data["is_searching_ranked"] = serializer.validated_data["is_searching_ranked"]
                request_data["min_opponent_points"] = serializer.validated_data["min_opponent_points"]

            return request_data, None

        except json.JSONDecodeError:
            return None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

    def _update_player_state(self, player, request_data):
        player.player_state = self.state
        if self.state == "in_queue":
            player.is_searching_ranked = request_data["is_searching_ranked"]
            player.min_opponent_points = request_data["min_opponent_points"]
        player.save()

    def _check_for_unaccepted_report(self, player: Player) -> bool:
        unaccepted_game = (
            Game.objects.filter(Q(player_1=player) | Q(player_2=player), is_waiting_confirmation=True)
            .exclude(who_created=player)
            .order_by("-id")
            .last()
        )
        if not unaccepted_game:
            return None

        return {
            unaccepted_game.player_1.nickname: unaccepted_game.castle_1,
            unaccepted_game.player_2.nickname: unaccepted_game.castle_2,
            "who_won": unaccepted_game.who_won.nickname,
        }

    def post(self, request, *args, **kwargs):
        try:
            if not self.state:
                return JsonResponse(
                    {"success": False, "error": "Invalid player state configuration"},
                    status=500,
                )

            request_data, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            try:
                player = Player.objects.get(nickname=request_data["nickname"])
            except Player.DoesNotExist:
                return JsonResponse({"success": False, "error": "Player profile not found"}, status=400)

            report_data = self._check_for_unaccepted_report(player)
            if report_data:
                return JsonResponse({"success": True, "report_data": report_data}, status=200)

            self._update_player_state(player, request_data)
            return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"Setting player state error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="60/m", method="POST", block=True), name="dispatch")
class RemoveFromQueueView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            required_fields = ["nickname", "is_accepted"]

            serializer = UserSerializer(data=data, required_fields=required_fields)
            if not serializer.is_valid():
                return None, JsonResponse({"success": False, "errors": serializer.errors}, status=400)

            return serializer.validated_data, None

        except json.JSONDecodeError:
            return None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

    def _get_player_object(self, nickname):
        try:
            return Player.objects.get(nickname=nickname)
        except Player.DoesNotExist:
            return JsonResponse({"success": False, "error": "Player profile not found"}, status=400)

    def _remove_player_from_queue(self, player, is_accepted):
        player.player_state = PlayerState.ACCEPTED if is_accepted else PlayerState.ONLINE
        player.save()
        if not is_accepted:
            with transaction.atomic():
                try:
                    game = Game.objects.filter(Q(player_1=player, is_new=True) | Q(player_2=player, is_new=True)).get()
                except Game.DoesNotExist:
                    return JsonResponse({"success": False, "error": "Queue has been declined"}, status=404)

                opponent = game.player_2 if player == game.player_1 else game.player_1
                opponent.player_state = PlayerState.IN_QUEUE
                opponent.save()
                game.delete()

        return JsonResponse({"success": True})

    def post(self, request, *args, **kwargs):
        try:
            request_data, error_response = self._parse_request_data(request)
            if error_response:
                return error_response

            player = self._get_player_object(request_data["nickname"])
            if isinstance(player, JsonResponse):
                return player

            return self._remove_player_from_queue(player, request_data["is_accepted"])

        except Exception as e:
            logger.error(f"Queue handling exception: {e}")
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
                nick: [ranking_points, player_state, is_ranked]
                for nick, ranking_points, player_state, is_ranked in players.values_list(
                    "nickname", "ranking_points", "player_state", "is_searching_ranked"
                )
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
@method_decorator(ratelimit(key="user_or_ip", rate="5/m", method=["POST"], block=True), name="dispatch")
class HandleMatchReport(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_post_data(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            game_serializer = GameReportSerializer(data=data, required_fields=["nicknames", "castles", "who_won"])

            if not game_serializer.is_valid():
                errors = {}
                errors.update(game_serializer.errors)
                return None, None, None, None, None, JsonResponse({"success": False, "errors": errors}, status=400)

            player_nickname = game_serializer.validated_data["nicknames"][0]
            opponent_nickname = game_serializer.validated_data["nicknames"][1]
            player_castle = game_serializer.validated_data["castles"][0]
            opponent_castle = game_serializer.validated_data["castles"][1]
            who_won = game_serializer.validated_data["who_won"]

            return player_nickname, opponent_nickname, player_castle, opponent_castle, who_won, None

        except json.JSONDecodeError:
            return None, None, None, None, None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

    def _create_match_report(self, player: Player, opponent: Player, player_castle: CastleType, opponent_castle: CastleType, who_won: Player):
        game = (
            Game.objects.filter((Q(player_1=player) | Q(player_2=player)) & (Q(is_new=True) | Q(is_waiting_confirmation=True)))
            .order_by("-id")
            .first()
        )
        players_data = {"message0": game.id if game else "No game found"}

        with transaction.atomic():
            if not game:
                game = Game.objects.create(player_1=player, player_2=opponent)

            if game.is_waiting_confirmation:
                if game.player_1 == player:
                    if game.castle_1 != player_castle or game.castle_2 != opponent_castle or game.who_won != who_won:
                        game.is_different = True
                else:
                    if game.castle_2 != player_castle or game.castle_1 != opponent_castle or game.who_won != who_won:
                        game.is_different = True

                if game.is_different:
                    game.is_waiting_confirmation = False
                    game.save()

                game.is_waiting_confirmation = False
                players_data = {"who_won": who_won.nickname}
                if game.is_ranked:
                    player_won = game.who_won
                    player_lost = game.player_2 if player_won == game.player_1 else game.player_1
                    if not game.points_change_winner and not game.points_change_loser:
                        game.points_change_winner, game.points_change_loser = self.__calculate_points_change(player_won, player_lost)
                    players_data[player_won.nickname] = game.points_change_winner
                    players_data[player_lost.nickname] = game.points_change_loser

                game.save()
                return players_data

            if game.is_new:
                if game.player_1 == player:
                    game.castle_1 = player_castle
                    game.castle_2 = opponent_castle
                else:
                    game.castle_2 = player_castle
                    game.castle_1 = opponent_castle
                game.who_won = who_won
                game.who_created = player
                game.is_new = False
                game.is_waiting_confirmation = True

            game.save()
            return None

    @staticmethod
    def __calculate_points_change(player_won: Player, player_lost: Player):
        X1 = player_won.ranking_points
        X2 = player_lost.ranking_points
        R1 = round(100 * (1 - (1 / (1 + 10 ** ((X2 - X1) / 1800)))) * (1 + (1000 - X1) / 2000))
        R2 = round(100 * (1 - (1 / (1 + 10 ** ((X2 - X1) / 1800)))))

        player_won.ranking_points += R1
        player_lost.ranking_points -= R2
        player_won.save()
        player_lost.save()

        return R1, R2

    def post(self, request, *args, **kwargs):
        try:
            (
                player_nickname,
                opponent_nickname,
                player_castle,
                opponent_castle,
                who_won,
                parse_error,
            ) = self._parse_post_data(request)
            if parse_error:
                return parse_error

            try:
                player = Player.objects.get(nickname=player_nickname)
                opponent = Player.objects.get(nickname=opponent_nickname)
                who_won = player if who_won == player.nickname else opponent
            except Player.DoesNotExist:
                return JsonResponse({"success": False, "error": "Player not found"}, status=400)

            data = self._create_match_report(player, opponent, player_castle, opponent_castle, who_won)

            return JsonResponse({"success": True, "data": data})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

        except Exception as e:
            logger.error(f"Creating match report error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(ratelimit(key="user_or_ip", rate="5/m", method=["GET", "POST"], block=True), name="dispatch")
class GetProfileInformation(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _parse_request_data(self, request):
        try:
            serializer = UserSerializer(data=request.GET, required_fields=["nickname"])
            if not serializer.is_valid():
                return (None, JsonResponse({"success": False, "errors": serializer.errors}, status=400))

            nickname = serializer.validated_data["nickname"]

            return nickname, None

        except json.JSONDecodeError:
            return (None, None, JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400))

    def get(self, request, *args, **kwargs):
        try:
            nickname, parse_error = self._parse_request_data(request)
            if parse_error:
                return parse_error

            try:
                player = Player.objects.get(nickname=nickname)
            except Player.DoesNotExist:
                return JsonResponse({"success": False, "error": "User not found"}, status=404)

            games_won_ranked = Game.objects.filter(Q(player_1=player) | Q(player_2=player), who_won=player, is_ranked=True).count()
            games_won_unranked = Game.objects.filter(Q(player_1=player) | Q(player_2=player), who_won=player, is_ranked=False).count()
            total_rankeds_won = Game.objects.filter(Q(player_1=player) | Q(player_2=player), is_ranked=True).count()
            total_unrankeds_won = Game.objects.filter(Q(player_1=player) | Q(player_2=player), is_ranked=False).count()

            player_information = {
                "ranking_points": player.ranking_points,
                "ranking_position": player.ranking_position,
                "ranked_games": [games_won_ranked, total_rankeds_won - games_won_ranked],
                "unranked_games": [games_won_unranked, total_unrankeds_won - games_won_unranked],
                "total_games": total_rankeds_won + total_unrankeds_won,
            }
            return JsonResponse({"success": True, "player_information": player_information})

        except Exception as e:
            logger.error(f"Password reset link error: {e}")
            return JsonResponse({"success": False, "error": "Something went wrong"}, status=500)
