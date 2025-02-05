import os
import toml
import easygui


def load_resolution_settings():
    return toml.load(os.path.join(os.getcwd(), "settings.toml"))["resolution"]


def load_game_settings():
    return toml.load(os.path.join(os.getcwd(), "settings.toml"))["game"]


def load_vpn_settings():
    return toml.load(os.path.join(os.getcwd(), "settings.toml"))["soft_ether"]


def check_for_missing_paths():
    is_saved = False
    with open(os.path.join(os.getcwd(), "settings.toml"), "r") as f:
        data = toml.load(f)
        if data["game"]["game_path"] == "":
            data["game"]["game_path"] == easygui.fileopenbox(
                msg="Plese select the path to AshanArena3.exe",
                title="AshanArena3",
                default=".exe",
            )
            is_saved = True

        if data["soft_ether"]["vpn_path"] == "":
            data["soft_ether"]["vpn_path"] = easygui.fileopenbox(
                msg="Plese select the path to SoftEtherVPN.exe",
                title="SoftEtherVPN",
                default=".exe",
            )
            is_saved = True

    if is_saved:
        with open(os.path.join(os.getcwd(), "settings.toml"), "w") as f:
            toml.dump(data, f)

    return data
