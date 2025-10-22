from django.contrib import admin
from django.db.models import Q

from h5_backend.models import Player, Game, Ban


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "ranking_points", "ranking_position", "player_state")
    list_filter = ("player_state",)
    ordering = ("-ranking_points",)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "player_1",
        "player_2",
        "castle_1",
        "castle_2",
        "points_change_winner",
        "points_change_loser",
        "who_won",
        "is_ranked",
        "is_waiting_confirmation",
        "is_different",
    )

    list_filter = (
        "is_ranked",
        "is_waiting_confirmation",
        "is_different",
    )

    search_fields = (
        "player_1__nickname",
        "player_2__nickname",
        "who_won__nickname",
        "castle_1",
        "castle_2",
    )


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "created_at", "duration")
    list_filter = ("created_at",)
