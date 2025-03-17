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
    # TODO: add flags for only one time repeat
    with open(os.path.join(os.getcwd(), "settings.toml"), "r") as f:
        data = toml.load(f)
        while True:
            path_str = str(data["game"]["game_path"]).lower()
            if "AshanArena3".lower() not in path_str:
                if data["game"]["game_path"] == "":
                    data["game"]["game_path"] == easygui.fileopenbox(
                        msg="Plese select the path to AshanArena3.exe",
                        title="AshanArena3",
                        default=".exe",
                    )
                    is_saved = True
            if "AshanArena3".lower() in path_str:
                break

        while True:
            path_str = str(data["soft_ether"]["vpn_path"]).lower()
            if "SoftEther".lower() not in path_str:
                data["soft_ether"]["vpn_path"] = easygui.fileopenbox(
                    msg="Plese select the path to SoftEtherVPN.exe",
                    title="SoftEtherVPN",
                    default=".exe",
                )
                is_saved = True
            if "SoftEther".lower() in path_str:
                break

    if is_saved:
        with open(os.path.join(os.getcwd(), "settings.toml"), "w") as f:
            toml.dump(data, f)

    return data
