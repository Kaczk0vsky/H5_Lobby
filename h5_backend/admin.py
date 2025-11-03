from django.contrib import admin
from django.db.models import Q

from h5_backend.models import Player, Game, Ban, OfflineMessage


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "ranking_points", "ranking_position", "player_state")
    list_filter = ("player_state",)
    ordering = ("-ranking_points",)
    search_fields = ("nickname",)


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

    list_filter = ("is_ranked", "is_waiting_confirmation", "is_different")
    search_fields = ("player_1__nickname", "player_2__nickname", "who_won__nickname", "castle_1", "castle_2")


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "created_at", "duration")
    list_filter = ("created_at",)
    search_fields = ("player__nickname",)


@admin.register(OfflineMessage)
class OfflineMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "event_type", "created_at")
    list_filter = ("created_at",)
    search_fields = ("recipient", "event_type")
