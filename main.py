from src.login import LoginWindow
import os
import django


def run_lobby():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_settings.settings")
    django.setup()
    lobby = LoginWindow()
    lobby.run_game()


if __name__ == "__main__":
    run_lobby()
