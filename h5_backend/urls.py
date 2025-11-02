from django.urls import path

from . import views


class SetPlayerOffline(views.SetPlayerStateView):
    state = "offline"


class SetPlayerOnline(views.SetPlayerStateView):
    state = "online"


urlpatterns = [
    path("get_csrf_token/", views.CsrfTokenView.as_view(), name="get_csrf_token"),
    path("register/", views.RegisterPlayer.as_view(), name="register_new_player"),
    path("login/", views.LoginPlayer.as_view(), name="login_player"),
    path("change_password/", views.GeneratePasswordResetLinkView.as_view(), name="change_password"),
    path("set_player_offline/", SetPlayerOffline.as_view(), name="set_player_offline"),
    path("set_player_online/", SetPlayerOnline.as_view(), name="set_player_online"),
    path("get_users_online/", views.UpdateUsersList.as_view(), name="update_users_list"),
    path("create_game_report/", views.HandleMatchReport.as_view(), name="handle_match_report"),
    path("get_profile/", views.GetProfileInformation.as_view(), name="get_profile"),
]
