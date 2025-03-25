from django.contrib import admin

from .models import Player, Game, PlayersMatched, Ban

admin.site.register(Player)
admin.site.register(Game)
admin.site.register(PlayersMatched)
admin.site.register(Ban)
