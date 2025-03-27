import os
import psutil
import time

from src.settings_reader import load_game_settings


class AschanArena3Game:
    def __init__(self, lobby: object):
        self.game_settings = load_game_settings()
        self.arena_process = "Arena3.exe"
        self.game_path = self.game_settings["game_path"]
        self.lobby = lobby

        os.startfile(os.path.join(self.game_path, "Arena3.exe"))

    def check_game_process(self):
        for process in psutil.process_iter():
            if process.name() == self.arena_process:
                return True
        return False

    def run_processes(self):
        self.lobby.minimize_to_tray()

        while True:
            is_running = self.check_game_process()
            time.sleep(0.5)
            if not is_running:
                break

        self.lobby.maximize_from_tray()
