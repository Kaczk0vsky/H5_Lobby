import pygame
import os
import requests
import sys

from src.settings_reader import load_resolution_settings
from src.global_vars import bg_sound_volume, env_dict
from widgets.button import Button
from widgets.cursor import Cursor


class BasicWindow:
    """
    A base class for creating a Pygame window with UI elements and pygame music handling.

    Attributes:
        text_color (str): Default text color.
        hovering_color (str): Color when hovering over UI elements.
        config (dict): Configuration settings loaded from the resolution settings.

    Methods:
        set_window_caption(title: str) -> None:
            Sets the Pygame window caption with a given title.

        play_background_music(music_path: str) -> None:
            Initializes Pygame audio and plays background music in a loop.

        stop_background_music() -> None:
            Stops and fades out the background music before quitting Pygame.

        get_font(font_size: int = 75) -> pygame.font.Font:
            Returns a font object with the specified size.

        create_window_elements(is_extended: bool = False) -> None:
            Loads and initializes background images and UI elements based on the extended mode.

        error_window(text: str) -> tuple:
            Creates and returns error message UI elements, including text and a back button.
    """

    def __init__(self):
        self.vpn_client = None
        self.text_color = "#d7fcd4"
        self.hovering_color = "White"
        self.config = load_resolution_settings()
        self.cursor = Cursor()

    def set_window_caption(self, title: str) -> None:
        pygame.display.set_caption(
            f"Heroes V of Might and Magic Ashan Arena 3 - {title}"
        )

    def play_background_music(self, music_path: str) -> None:
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.Channel(0).play(
            pygame.mixer.Sound(os.path.join(os.getcwd(), music_path)),
            -1,
            0,
        )
        pygame.mixer.Channel(0).set_volume(bg_sound_volume)

    def stop_background_music(self) -> None:
        pygame.mixer.fadeout(5000)
        pygame.quit()

    def quit_game_handling(self):
        if self.vpn_client is not None:
            self.vpn_client.set_vpn_state(False)
            url = f"http://{env_dict["SERVER_URL"]}:8000/set_player_offline/"
            user_data = {"nickname": self.vpn_client.user_name}
            requests.post(url, json=user_data)
        pygame.quit()
        sys.exit()

    def get_font(self, font_size: int = 75) -> pygame.font.Font:
        return pygame.font.Font("resources/Quivira.otf", font_size)

    def create_window_elements(self, is_extended: bool = False) -> None:
        self.BG = pygame.image.load(
            os.path.join(os.getcwd(), "resources/background/background.png")
        )
        self.SMALLER_WINDOWS_BG = pygame.image.load(
            os.path.join(os.getcwd(), "resources/game_search/game_search_window.png")
        )
        self.BUTTON = pygame.image.load(
            os.path.join(
                os.getcwd(), "resources/game_search/cancel_search_button_dark.png"
            )
        )
        self.BUTTON_HIGHLIGHTED = pygame.image.load(
            os.path.join(
                os.getcwd(),
                "resources/game_search/cancel_search_button_highlighted.png",
            )
        )

        if is_extended:
            self.PLAYER_LIST = pygame.image.load(
                os.path.join(os.getcwd(), "resources/background/players_online.png")
            )
            self.TOP_BAR = pygame.image.load(
                os.path.join(os.getcwd(), "resources/main_menu/top_bar.png")
            )
            self.NEWS = pygame.image.load(
                os.path.join(os.getcwd(), "resources/news/news_window.png")
            )
            self.QUIT = pygame.image.load(
                os.path.join(os.getcwd(), "resources/buttons/close_dark.png")
            )
            self.QUIT_HIGHLIGHTED = pygame.image.load(
                os.path.join(os.getcwd(), "resources/buttons/close_highlighted.png")
            )
            self.ICON_SQUARE = pygame.image.load(
                os.path.join(os.getcwd(), "resources/buttons/iconsquare_dark.png")
            )
            self.ICON_SQUARE_HIGHLIGHTED = pygame.image.load(
                os.path.join(
                    os.getcwd(), "resources/buttons/iconsquare_highlighted.png"
                )
            )
            self.OPTIONS = pygame.image.load(
                os.path.join(os.getcwd(), "resources/buttons/options_dark.png")
            )
            self.OPTIONS_HIGHLIGHTED = pygame.image.load(
                os.path.join(os.getcwd(), "resources/buttons/options_highlighted.png")
            )
            self.SCROLL = pygame.image.load(
                os.path.join(os.getcwd(), "resources/buttons/scroll.png")
            )
            self.CANCEL_BUTTON = pygame.image.load(
                os.path.join(os.getcwd(), "resources/game_search/red_button_dark.png")
            )
            self.CANCEL_BUTTON_HIGHLIGHTED = pygame.image.load(
                os.path.join(
                    os.getcwd(), "resources/game_search/red_button_highlighted.png"
                )
            )
            self.ACCEPT_BUTTON = pygame.image.load(
                os.path.join(os.getcwd(), "resources/game_search/green_button_dark.png")
            )
            self.ACCEPT_BUTTON_HIGHLIGHTED = pygame.image.load(
                os.path.join(
                    os.getcwd(), "resources/game_search/green_button_highlighted.png"
                )
            )

    def error_window(self, text: str) -> tuple:
        overlay_width, overlay_height = (
            600,
            400,
        )
        self.SMALLER_WINDOWS_BG = pygame.transform.scale(
            self.SMALLER_WINDOWS_BG, (overlay_width, overlay_height)
        )

        WRONG_PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
            text, True, self.text_color
        )
        WRONG_PASSOWRD_RECT = WRONG_PASSWORD_TEXT.get_rect(
            center=(
                self.SCREEN.get_width() / 2,
                self.SCREEN.get_height() / 2.5,
            )
        )

        BACK_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            pos=(self.SCREEN.get_width() / 2, self.SCREEN.get_height() / 1.5),
            text_input="Back",
            font=self.get_font(self.font_size[0]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )

        return (WRONG_PASSWORD_TEXT, WRONG_PASSOWRD_RECT, BACK_BUTTON)
