from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.cache import cache

from h5_backend.models import Player, Game, PlayerState
from h5_backend.notifications import notify_users_list_change


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(nickname=instance.username)


@receiver(post_delete, sender=User)
def delete_player(sender, instance, **kwargs):
    Player.objects.filter(nickname=instance.username).delete()


@receiver(pre_delete, sender=Game)
def delete_game(sender, instance, **kwargs):
    if instance.who_won and instance.points_change_winner is not None and instance.points_change_loser is not None:
        who_lost = instance.player_2 if instance.who_won == instance.player_1 else instance.player_1

        instance.who_won.ranking_points -= instance.points_change_winner
        who_lost.ranking_points += instance.points_change_loser

        instance.who_won.save()
        who_lost.save()


@receiver(post_save, sender=Player)
def update_user_list(sender, instance, **kwargs):
    current_users = Player.objects.exclude(player_state=PlayerState.OFFLINE)
    current_users_formatted = {
        nick: [ranking_points, player_state, is_ranked]
        for nick, ranking_points, player_state, is_ranked in current_users.values_list(
            "nickname", "ranking_points", "player_state", "is_searching_ranked"
        )
    }
    previous_users_formatted = cache.get("previous_users_formatted") or {}

    if not current_users_formatted == previous_users_formatted:
        for player in current_users:
            notify_users_list_change(player, current_users_formatted)

    cache.set("previous_users_formatted", current_users_formatted, timeout=None)
