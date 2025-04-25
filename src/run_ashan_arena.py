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

    def load_console_file(self):
        path = os.path.join(self.game_settings["game_path"], "console.txt")

        if os.path.exists(path):
            data = {}
            with open(path, "r") as file:
                for line in file:
                    splitted_str = line.strip("\n").split("=")
                    data[splitted_str[0]] = splitted_str[1]

            if data["player_won"] == "true":
                self.lobby.handle_match_report(is_won=True, castle=data["castle"])
            elif data["player_won"] == "false":
                self.lobby.handle_match_report(is_won=False, castle=data["castle"])
            # os.remove(path)

    def run_processes(self):
        self.lobby.minimize_to_tray()

        while True:
            is_running = self.check_game_process()
            time.sleep(2)
            if not is_running:
                break

        self.lobby.maximize_from_tray()
        self.load_console_file()
