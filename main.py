import os
import sys

from pathlib import Path

from src.settings_writer import check_for_missing_paths
from src.login_manager import LoginWindow

USER_DIR = Path.home() / ".H5_Lobby"
USER_DIR.mkdir(exist_ok=True)

BASE_PATH = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def run_lobby():
    check_for_missing_paths()
    lobby = LoginWindow()
    lobby.run_login()


if __name__ == "__main__":
    run_lobby()
