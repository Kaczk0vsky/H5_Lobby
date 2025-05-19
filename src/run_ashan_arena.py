import os
import psutil
import time
import subprocess
import keyboard
import json

from src.settings_reader import load_game_settings
from src.decorators import run_in_thread


class AschanArena3Game:
    __is_running = True
    __closed_unintentionally = False
    __closed_intentionally = False
    __key_pressed = None
    __prev_key_pressed = None

    def __init__(self, lobby: object):
        self.game_settings = load_game_settings()
        self.arena_process = "Arena3.exe"
        self.lobby = lobby

        command = os.path.join(self.game_settings["game_path"], "Arena3.exe")
        self.process = subprocess.Popen(command, cwd=self.game_settings["game_path"])

    def check_game_process(self):
        for process in psutil.process_iter():
            if process.name() == self.arena_process:
                return True
        return False

    @run_in_thread
    def check_keys_pressed(self):
        while self.__is_running:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                self.__prev_key_pressed = self.__key_pressed
                self.__key_pressed = event.name

            # Checking if game was closed with alt + f4
            if self.__key_pressed == "f4" and self.__prev_key_pressed == "alt":
                returncode = self.process.poll()
                if returncode is not None:
                    print(f"Game closed: {returncode}.")
                    if returncode == 0:
                        self.__closed_intentionally = True
                        self.__is_running = False
                    else:
                        self.__closed_unintentionally = True
                        self.__is_running = False
                return

    @run_in_thread
    def check_if_crashed(self):
        time.sleep(5)
        while self.__is_running:
            returncode = self.process.poll()
            if returncode is not None:
                if returncode != 0:
                    print(f"Game crashed: {returncode}.")
                    self.__closed_unintentionally = True
                    self.__is_running = False
                break
            time.sleep(2)

    @run_in_thread
    def check_if_disconnected(self):
        # Get-NetAdapter -Name 'VPN - VPN Client' | ConvertTo-Json
        # Get-NetAdapterStatistics -Name 'Wi-Fi' | ConvertTo-Json
        command = ["powershell", "-Command", f"Get-NetAdapterStatistics -Name 'Wi-Fi' | ConvertTo-Json"]
        packets = [None, None]

        while self.__is_running:
            try:
                # Check if player has disconnected
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                stats = json.loads(result.stdout)
                last_packets = packets
                packets = [stats["ReceivedUnicastBytes"], stats["SentUnicastBytes"]]

                if last_packets == packets:
                    print("Disconnect due to lost connection.")
                    self.__closed_unintentionally = True
                    self.__is_running = False

                time.sleep(2)
            except subprocess.CalledProcessError as e:
                print("PowerShell Error:", e)
            except json.JSONDecodeError:
                print("Parsing error - check permissions")

    def load_console_file(self):
        path = os.path.join(self.game_settings["game_path"], "console.txt")

        if os.path.exists(path):
            data = {}
            with open(path, "r") as file:
                for line in file:
                    splitted_str = line.strip("\n").split("=")
                    data[splitted_str[0]] = splitted_str[1]

            if self.__closed_intentionally:
                self.lobby.handle_match_report(is_won=False, castle=None)
                self.__closed_intentionally = False
            elif self.__closed_unintentionally:
                self.__closed_unintentionally = False
            elif data["player_won"] == "true":
                self.lobby.handle_match_report(is_won=True, castle=data["castle"])
            elif data["player_won"] == "false":
                self.lobby.handle_match_report(is_won=False, castle=data["castle"])
            # os.remove(path)

    def run_processes(self):
        self.lobby.minimize_to_tray()
        self.check_keys_pressed()
        self.check_if_crashed()
        self.check_if_disconnected()

        while True:
            self.__is_running = self.check_game_process()
            time.sleep(2)
            if not self.__is_running:
                break

        self.lobby.maximize_from_tray()
        self.load_console_file()
