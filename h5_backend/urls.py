from django.urls import path

from . import views


class SetPlayerOffline(views.SetPlayerStateView):
    state = "offline"


class SetPlayerOnline(views.SetPlayerStateView):
    state = "online"


class AddPlayerToQueue(views.SetPlayerStateView):
    state = "in_queue"


class RemovePlayerFromQueue(views.QueueHandlerView):
    action = "remove_player"


class GetPlayersMatched(views.QueueHandlerView):
    action = "match_players"


class CheckIfOpponentAccepted(views.QueueHandlerView):
    action = "check_opponent_state"


urlpatterns = [
    path("get_csrf_token/", views.CsrfTokenView.as_view(), name="get_csrf_token"),
    path("register/", views.RegisterPlayer.as_view(), name="register_new_player"),
    path("login/", views.LoginPlayer.as_view(), name="login_player"),
    path("change_password/", views.GeneratePasswordResetLinkView.as_view(), name="change_password"),
    path("set_player_offline/", SetPlayerOffline.as_view(), name="set_player_offline"),
    path("set_player_online/", SetPlayerOnline.as_view(), name="set_player_online"),
    path("add_to_queue/", AddPlayerToQueue.as_view(), name="add_to_queue"),
    path("remove_from_queue/", RemovePlayerFromQueue.as_view(), name="remove_from_queue"),
    path("get_players_matched/", GetPlayersMatched.as_view(), name="get_players_matched"),
    path("check_if_oponnent_accepted/", CheckIfOpponentAccepted.as_view(), name="check_if_oponnent_accepted"),
    path("get_users_online/", views.UpdateUsersList.as_view(), name="update_users_list"),
    path("create_game_report/", views.HandleMatchReport.as_view(), name="handle_match_report"),
    path("get_profile/", views.GetProfileInformation.as_view(), name="get_profile"),
]
