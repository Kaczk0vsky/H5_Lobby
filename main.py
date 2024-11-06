from src.login import LoginWindow


def run_lobby():
    """Run the H5_Lobby GUI."""
    lobby = LoginWindow()
    lobby.run_game()


if __name__ == "__main__":
    run_lobby()
