import os

from src.settings_reader import load_game_settings


class AschanArena3_Game:
    def __init__(self):
        self.game_settings = load_game_settings()
        self.game_path = self.game_settings["game_path"]
        os.startfile(os.path.join(self.game_path, "AshanArena3.exe"))

    def run_processes(self):
        pass
