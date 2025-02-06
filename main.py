import os
import django

from src.settings_writer import check_for_missing_paths
from src.login import LoginWindow


def run_lobby():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_settings.settings")
    django.setup()
    check_for_missing_paths()
    lobby = LoginWindow()
    lobby.run_game()


if __name__ == "__main__":
    run_lobby()
