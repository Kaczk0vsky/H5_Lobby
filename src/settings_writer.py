import os
import toml
import easygui


def save_login_information(user_data: dict):
    with open(os.path.join(os.getcwd(), "settings.toml"), "r") as f:
        data = toml.load(f)
        if user_data["remember_password"]:
            data["client_settings"]["nickname"] = str(user_data["nickname"])
            data["client_settings"]["password"] = str(user_data["password"])
        else:
            data["client_settings"]["nickname"] = ""
            data["client_settings"]["password"] = ""
        data["client_settings"]["remember_password"] = bool(
            user_data["remember_password"]
        )

    with open(os.path.join(os.getcwd(), "settings.toml"), "w") as f:
        toml.dump(data, f)


def check_for_missing_paths() -> dict:
    is_saved = False
    with open(os.path.join(os.getcwd(), "settings.toml"), "r") as f:
        data = toml.load(f)
        path_str = str(data["game"]["game_path"]).lower()
        if "bin".lower() not in path_str:
            data["game"]["game_path"] = easygui.diropenbox(
                msg="Plese select the path to directory with Arena3.exe",
                title="AshanArena3",
                default="*",
            )
            is_saved = True

        path_str = str(data["soft_ether"]["vpn_path"]).lower()
        if "SoftEther".lower() not in path_str:
            data["soft_ether"]["vpn_path"] = easygui.diropenbox(
                msg="Plese select the path to directory with SoftEtherVPN.exe",
                title="SoftEtherVPN",
            )
            is_saved = True

    if is_saved:
        with open(os.path.join(os.getcwd(), "settings.toml"), "w") as f:
            toml.dump(data, f)

    return data
