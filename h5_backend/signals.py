from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.cache import cache

from h5_backend.models import Player, Game, PlayerState
from h5_backend.notifications import notify_users_list_change, notify_report_data


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


@receiver(pre_save, sender=Game)
def send_report(sender, instance, **kwargs):
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if instance.who_won and old.is_waiting_confirmation and not instance.is_waiting_confirmation:
        opponent = instance.player_1 if instance.who_created == instance.player_2 else instance.player_2
        notify_report_data(opponent, instance)


@receiver(pre_save, sender=Player)
def cache_old_points(sender, instance, **kwargs):
    if instance.pk:
        instance._old_points = Player.objects.get(pk=instance.pk).ranking_points
    else:
        instance._old_points = None


@receiver(post_save, sender=Player)
def update_ranking_positions(sender, instance, created, **kwargs):
    old = getattr(instance, "_old_points", None)
    if not created and old == instance.ranking_points:
        return

    with transaction.atomic():
        players = Player.objects.order_by("-ranking_points", "id")

        updates = []
        position = 1

        for player in players:
            if player.ranking_position != position:
                player.ranking_position = position
                updates.append(player)
            position += 1

        if updates:
            Player.objects.bulk_update(updates, ["ranking_position"])
