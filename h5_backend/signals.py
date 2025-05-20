from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from h5_backend.models import Player, Game


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
