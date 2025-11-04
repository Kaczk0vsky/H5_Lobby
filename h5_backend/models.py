from django.db import models
from django.utils import timezone
from datetime import timedelta


class PlayerState(models.TextChoices):
    OFFLINE = "offline", "Offline"
    ONLINE = "online", "Online"
    IN_QUEUE = "in_queue", "In Queue"
    WAITING_ACCEPTANCE = "waiting_acceptance", "Waiting Acceptance"
    ACCEPTED = "accepted", "Accepted"
    PLAYING = "playing", "Playing"


class CastleType(models.TextChoices):
    HEAVEN = "haven", "Haven"
    INFERNO = "inferno", "Inferno"
    NECROPOLIS = "necropolis", "Necropolis"
    SYLVAN = "sylvan", "Sylvan"
    DUNGEON = "dungeon", "Dungeon"
    ACADEMY = "academy", "Academy"
    FORTRESS = "fortress", "Fortress"
    STRONGHOLD = "stronghold", "Stronghold"


class Player(models.Model):
    # unique id
    id = models.AutoField(primary_key=True)
    # player nickname
    nickname = models.CharField(editable=True, max_length=30, unique=True)
    # ranking points
    ranking_points = models.IntegerField(editable=True, default=1000)
    # leaderboard position
    ranking_position = models.IntegerField(editable=False, unique=True, null=True)
    # player state in lobby
    player_state = models.CharField(max_length=30, choices=PlayerState.choices, default=PlayerState.OFFLINE, editable=True)
    # if player is looking to play ranked game
    is_searching_ranked = models.BooleanField(editable=True, default=True)
    # minimal opponent points in searching
    min_opponent_points = models.IntegerField(editable=True, default=0)
    # for ws connection purposes
    connected_to_ws = models.BooleanField(editable=True, default=False)

    def __str__(self):
        return f"{self.nickname} - {self.ranking_points} ({self.player_state})"


class Game(models.Model):
    # unique id
    id = models.BigAutoField(primary_key=True)
    # players
    player_1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        editable=True,
        null=True,
        blank=True,
        db_column="player_1",
        related_name="game_as_player_1",
    )
    player_2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        editable=True,
        null=True,
        blank=True,
        db_column="player_2",
        related_name="game_as_player_2",
    )
    castle_1 = models.CharField(
        max_length=20,
        choices=CastleType.choices,
        editable=True,
        null=True,
        blank=True,
    )
    castle_2 = models.CharField(
        max_length=20,
        choices=CastleType.choices,
        editable=True,
        null=True,
        blank=True,
    )
    points_change_winner = models.IntegerField(editable=True, default=0)
    points_change_loser = models.IntegerField(editable=True, default=0)

    # who won
    who_won = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        editable=True,
        related_name="player_who_won",
        null=True,
        blank=True,
    )
    # who created the report
    who_created = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        editable=True,
        related_name="player_who_created",
        null=True,
        blank=True,
    )

    is_new = models.BooleanField(default=True)
    is_ranked = models.BooleanField(default=True)
    is_waiting_confirmation = models.BooleanField(default=False)
    is_different = models.BooleanField(default=False)

    def __str__(self):
        return f"Game ID - {self.id}, Won by - {self.who_won}"


class Ban(models.Model):
    id = models.AutoField(primary_key=True)
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        editable=True,
        null=True,
        blank=True,
        db_column="player_banned",
        related_name="ban_for_player",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(default=timedelta(days=7))

    def get_time_left(self):
        expiration_time = self.created_at + self.duration
        time_remaining = expiration_time - timezone.now()
        return max(time_remaining, timedelta(0))

    def __str__(self):
        return f"Player {self.player} - {self.get_time_left()}"


class OfflineMessage(models.Model):
    recipient = models.ForeignKey("Player", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
