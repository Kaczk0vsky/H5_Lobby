from django.urls import path

from . import views

urlpatterns = [
    path("ashanarena", views.ashanarena, name="ashanarena"),
    path("with_celery", views.with_celery, name="with_celery"),
]
