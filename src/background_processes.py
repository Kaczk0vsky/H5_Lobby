import os

from src.decorators import run_in_thread
from src.settings_reader import load_game_settings


class BackgroundProcesses:
    def __init__(self):
        self.game_settings = load_game_settings()
        self.game_path = self.game_settings["game_path"]

    @run_in_thread
    def scan_for_info(self):
        if os.path.exists(os.path.join(self.game_path, "console.txt")):
            pass

        # os.remove(self.game_path)

    def run_background_processes(self):
        self.scan_for_info()
