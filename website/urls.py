from django.urls import path

from . import views

urlpatterns = [
    path("", views.ashanarena, name=""),
    path(
        "reset/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
]
