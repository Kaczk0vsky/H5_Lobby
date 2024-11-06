from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_new_player, name="register_new_player"),
]
