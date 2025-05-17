import os
import toml


def load_game_settings():
    return toml.load(os.path.join(os.getcwd(), "settings.toml"))["game"]


def load_vpn_settings():
    return toml.load(os.path.join(os.getcwd(), "settings.toml"))["soft_ether"]


def load_user():
    return toml.load(os.path.join(os.getcwd(), "settings.toml"))["user"]


def load_client_settings():
    return toml.load(os.path.join(os.getcwd(), "settings.toml"))["client_settings"]
