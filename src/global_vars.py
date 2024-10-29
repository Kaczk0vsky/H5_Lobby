import os
import toml

def load_initial_window_setting():
    return toml.load(os.path.join(os.getcwd(), "settings.toml"))["initial_window"]
