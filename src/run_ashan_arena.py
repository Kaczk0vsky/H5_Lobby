from src.settings_reader import load_game_settings

import os


class AschanArena3_Game:
    def __init__(self):
        self.game_settings = load_game_settings()
        self.game_path = self.game_settings["game_path"]
        os.startfile(self.game_path)

    def run_processes(self):
        pass
