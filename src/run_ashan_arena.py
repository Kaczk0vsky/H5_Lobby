import os
import psutil
import time
import subprocess
import keyboard
import json

from src.settings_reader import load_game_settings
from src.decorators import run_in_thread
from src.helpers import check_server_connection


class AschanArena3Game:
    __is_running = True
    __closed_unintentionally = False
    __closed_intentionally = False
    __key_pressed = None
    __prev_key_pressed = None
    _has_disconnected = False
    _reconnect_back_to_game = False

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
                    self._reconnect_back_to_game = True
                    self._has_disconnected = True
                    self.__is_running = False
                break
            time.sleep(2)

    @run_in_thread
    def check_if_disconnected(self):
        # Get list of network adapters
        command = ["powershell", "-Command", "Get-NetAdapterStatistics | Select-Object Name | ConvertTo-Json -Depth 3"]
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding="utf-8")
        net_adapters = json.loads(result.stdout)
        adapter_names = {}
        for adapter in net_adapters:
            for value in adapter.values():
                adapter_names[value] = {
                    "ReceivedUnicastBytes": None,
                    "SentUnicastBytes": None,
                    "PreviousReceivedUnicastBytes": None,
                    "PreviousSentUnicastBytes": None,
                }

        if adapter_names is None:
            print("Network adapters not found...")
            return

        while self.__is_running:
            try:
                player_connected = False
                for key, value in adapter_names.items():
                    command = ["powershell", "-Command", f"Get-NetAdapterStatistics -Name '{key}' | ConvertTo-Json"]
                    result = subprocess.run(command, capture_output=True, text=True, check=True)
                    stats = json.loads(result.stdout)
                    value["PreviousReceivedUnicastBytes"] = value["ReceivedUnicastBytes"]
                    value["PreviousSentUnicastBytes"] = value["SentUnicastBytes"]
                    value["ReceivedUnicastBytes"] = stats["ReceivedUnicastBytes"]
                    value["SentUnicastBytes"] = stats["SentUnicastBytes"]
                    if (
                        value["PreviousReceivedUnicastBytes"] != value["ReceivedUnicastBytes"]
                        and value["PreviousSentUnicastBytes"] != value["SentUnicastBytes"]
                    ):
                        player_connected = True

                # Check if player has disconnected
                if not player_connected:
                    print("Disconnect due to lost connection.")
                    self.__closed_unintentionally = True
                    self._reconnect_back_to_game = True
                    self._has_disconnected = True
                    self.__is_running = False

                time.sleep(10)
            except subprocess.CalledProcessError as e:
                print("PowerShell Error:", e)
            except json.JSONDecodeError:
                print("Parsing error - check permissions")

    def load_console_file(self):
        if self.__closed_unintentionally:
            self.__closed_unintentionally = False
            return

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
            elif data["player_won"] == "true":
                self.lobby.handle_match_report(is_won=True, castle=data["castle"])
            elif data["player_won"] == "false":
                self.lobby.handle_match_report(is_won=False, castle=data["castle"])
            # os.remove(path)

    def run_processes(self):
        self.lobby.minimize_to_tray()
        time.sleep(5)  # Wait for game to open
        self.check_keys_pressed()
        self.check_if_crashed()
        self.check_if_disconnected()
        while self.__is_running:
            try:
                self.__is_running = self.check_game_process()
                time.sleep(2)
            except:
                break

        if not self._reconnect_back_to_game:
            self.lobby.set_player_online()

        self.lobby.maximize_from_tray()
        self.load_console_file()
