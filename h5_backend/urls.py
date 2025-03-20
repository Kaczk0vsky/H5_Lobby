from django.urls import path

from . import views

urlpatterns = [
    path("ashanarena/", views.ashanarena, name="ashanarena"),
    path("register/", views.register_new_player, name="register_new_player"),
    path("login/", views.login_player, name="login_player"),
    path("change_password/", views.change_password, name="change_password"),
    path("set_player_offline/", views.set_player_offline, name="set_player_offline"),
    path("add_to_queue/", views.add_to_queue, name="add_to_queue"),
    path("remove_from_queue/", views.remove_from_queue, name="remove_from_queue"),
    path("get_players_matched/", views.get_players_matched, name="get_players_matched"),
    path(
        "check_if_opponent_accepted/",
        views.check_if_opponent_accepted,
        name="check_if_opponent_accepted",
    ),
]
