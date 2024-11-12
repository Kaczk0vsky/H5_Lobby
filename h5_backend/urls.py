from django.urls import path

from . import views

urlpatterns = [
    path("ashanarena", views.ashanarena, name="ashanarena"),
]
