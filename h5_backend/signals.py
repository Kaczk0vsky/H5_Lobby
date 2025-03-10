from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from h5_backend.models import Player


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        # Automatically create a Player instance when a new User is created
        Player.objects.create(nickname=instance.username)


@receiver(post_delete, sender=User)
def delete_player(sender, instance, **kwargs):
    Player.objects.filter(nickname=instance.username).delete()
