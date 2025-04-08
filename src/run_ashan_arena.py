import os
import psutil
import time
import subprocess

from src.settings_reader import load_game_settings


class AschanArena3Game:
    def __init__(self, lobby: object):
        self.game_settings = load_game_settings()
        self.arena_process = "Arena3.exe"
        self.lobby = lobby

        command = f'cd /d "{self.game_settings["game_path"]}" && start Arena3.exe'
        subprocess.Popen(command, shell=True)

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
