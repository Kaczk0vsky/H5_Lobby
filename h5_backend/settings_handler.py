import os
import toml


def load_server_settings():
    return toml.load(os.path.join(os.getcwd(), "settings.toml"))["H5_Server"]


def save_server_settings():
    settings_file_path = os.path.join(os.getcwd(), "h5_backend/settings.toml")

    try:
        with open(settings_file_path, "r") as file:
            settings = toml.load(file)
    except FileNotFoundError:
        return

    settings["H5_Server"] = settings.get("H5_Server", {})
    ip_string = settings["H5_Server"]["last_available_ip"].split(".")
    ip_string[3] = str(int(ip_string[3]) + 1)
    settings["H5_Server"]["last_available_ip"] = ".".join(ip_string)

    with open(os.path.join(os.getcwd(), "/h5_backend/settings.toml"), "w") as file:
        toml.dump(settings, file)
