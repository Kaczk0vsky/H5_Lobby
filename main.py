import os
import shutil
import sys

from pathlib import Path

from src.settings_writer import check_for_missing_paths
from src.login import LoginWindow

USER_DIR = Path.home() / ".H5_Lobby"
USER_DIR.mkdir(exist_ok=True)

BASE_PATH = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

ENV_SRC = Path(BASE_PATH) / ".env"
ENV_DEST = USER_DIR / ".env"

if not ENV_DEST.exists():
    shutil.copy(ENV_SRC, ENV_DEST)
    ENV_DEST.chmod(0o444)


def run_lobby():
    check_for_missing_paths()
    lobby = LoginWindow()
    lobby.run_game()


if __name__ == "__main__":
    run_lobby()
