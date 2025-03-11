from src.settings_writer import check_for_missing_paths
from src.login import LoginWindow


def run_lobby():
    # Check if the path to everything was given
    check_for_missing_paths()

    # Starting the client
    lobby = LoginWindow()
    lobby.run_game()


if __name__ == "__main__":
    run_lobby()
