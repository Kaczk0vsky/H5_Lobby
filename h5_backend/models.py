from django.db import models


class Player(models.Model):
    # unique id
    id = models.IntegerField(editable=False, primary_key=True, unique=True)
    # player nickname
    nickname = models.CharField(editable=True, max_length=30, unique=True)
    # ranking points
    ranking_points = models.IntegerField(editable=True, default=1000)
    # leaderboard position
    ranking_position = models.IntegerField(editable=False, unique=True, null=True)

    OFFLINE = "offline"
    ONLINE = "online"
    BANNED = "banned"
    PLAYING = "playing"

    PLAYER_STATE_CHOICES = [
        (OFFLINE, "offline"),
        (ONLINE, "online"),
        (BANNED, "banned"),
        (PLAYING, "playing"),
    ]
    # player state
    player_state = models.CharField(
        max_length=30, choices=PLAYER_STATE_CHOICES, default="offline", editable=True
    )

    def __str__(self):
        return f"{self.nickname} - {self.ranking_points} ({self.player_state})"


# Create your models here.
class Game(models.Model):
    # unique id
    id = models.IntegerField(editable=False, primary_key=True, unique=True)
    # players
    player_1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        editable=True,
        null=True,
        blank=True,
        db_column="player_1",
        related_name="game_as_player_1",  # Unique related_name for player_1
    )
    player_2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        editable=True,
        null=True,
        blank=True,
        db_column="player_2",
        related_name="game_as_player_2",  # Unique related_name for player_2
    )
    # castles
    HEAVEN = "heaven"
    INFERNO = "inferno"
    NECROPOLIS = "necropolis"
    SYLVAN = "sylvan"
    DUNGEON = "dungeon"
    ACADEMY = "academy"
    FORTRESS = "fortress"
    STRONGHOLD = "stronghold"

    CASTLE_TYPE_CHOICES = [
        (HEAVEN, "heaven"),
        (INFERNO, "inferno"),
        (NECROPOLIS, "necropolis"),
        (SYLVAN, "sylvan"),
        (DUNGEON, "dungeon"),
        (ACADEMY, "academy"),
        (FORTRESS, "fortress"),
        (STRONGHOLD, "stronghold"),
    ]
    castle_1 = models.CharField(
        max_length=20, choices=CASTLE_TYPE_CHOICES, default="heaven", editable=True
    )
    castle_2 = models.CharField(
        max_length=20, choices=CASTLE_TYPE_CHOICES, default="heaven", editable=True
    )

    # who won
    who_won = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        editable=True,
        null=False,
        blank=False,
        related_name="player_who_won",  # Unique related_name for who_won
    )
    points_change = models.IntegerField(
        editable=False,
        null=True,
    )

    def __str__(self):
        return f"Game ID - {self.id}, Won by - {self.who_won}"
