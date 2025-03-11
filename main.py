import os
import django

from src.settings_writer import check_for_missing_paths
from src.login import LoginWindow


def run_lobby():
    # Ensuring that django is beeing loaded before start
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_settings.settings")
    django.setup()

    # Check if the path to everything was given
    check_for_missing_paths()

    # Starting the client
    lobby = LoginWindow()
    lobby.run_game()


if __name__ == "__main__":
    run_lobby()
