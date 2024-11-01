#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
from src.login import LoginWindow

import os
import threading
import sys


def run_django_server():
    """Run Django development server."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_settings.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Running the backend from that line
    execute_from_command_line(
        ["manage.py", "runserver", "127.0.0.1:8000", "--noreload"]
    )
    from django.core.management import execute_from_command_line

    # for creating super user disable the line above and uncomment this below
    # execute_from_command_line(sys.argv)


def run_lobby():
    """Run the H5_Lobby GUI."""
    lobby = LoginWindow()
    lobby.run_game()


def main():
    # Start Django server in a separate thread
    django_thread = threading.Thread(target=run_django_server)
    django_thread.daemon = True  # Allows program to exit even if thread is running
    django_thread.start()

    # Run lobby GUI in the main thread
    run_lobby()


if __name__ == "__main__":
    main()
