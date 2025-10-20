import re

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import serializers

from h5_backend.models import Game, CastleType


class UserSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=16, required=True)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    min_opponent_points = serializers.IntegerField(required=False)
    is_searching_ranked = serializers.BooleanField(required=False)
    is_accepted = serializers.BooleanField(required=False)

    def __init__(self, *args, required_fields=None, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_nickname(self, value):
        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", value):
            raise serializers.ValidationError("Invalid nickname format")
        return value

    def validate_password(self, value):
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d#$%^+=!]{8,}$", value):
            raise serializers.ValidationError("Password must be at least 8 characters and include letters and numbers and one special character")
        return value

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        return value


class GameReportSerializer(serializers.Serializer):
    nicknames = serializers.ListField(
        child=serializers.CharField(max_length=16), min_length=2, max_length=2, required=True, help_text="List of two nicknames: [player1, player2]"
    )
    castles = serializers.ListField(
        child=serializers.ChoiceField(choices=CastleType.choices),
        min_length=2,
        max_length=2,
        required=True,
        help_text="List of two castles: [castle1, castle2]",
    )
    who_won = serializers.CharField(max_length=16, required=True, help_text="Nickname of the player who won: player1")

    def __init__(self, *args, required_fields=None, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, data):
        nicknames = data.get("nicknames", [])
        castles = data.get("castles", [])

        if len(nicknames) != len(castles):
            raise serializers.ValidationError("Number of nicknames and castles must match")

        return data
