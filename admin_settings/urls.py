"""
URL configuration for admin_settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from h5_backend import views

urlpatterns = [
    path("", include("h5_backend.urls")),
    path("admin/", admin.site.urls),
    path("register/", views.register_new_player, name="register_new_player"),
    path("login/", views.login_player, name="login_player"),
    path("set_player_offline/", views.set_player_offline, name="set_player_offline"),
]
