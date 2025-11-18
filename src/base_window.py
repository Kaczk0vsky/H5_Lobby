import pygame
import os
import requests
import sys

from src.settings_reader import load_client_settings
from src.global_vars import env_dict, transformation_factors
from src.helpers import render_small_caps
from widgets.button import Button
from widgets.cursor import Cursor
from utils.logger import get_logger

logger = get_logger(__name__)


class GameWindowsBase:
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

        create_universal_elements() -> None:
            Loads and initializes background images and UI elements for both windows.

        create_login_elements() -> None:
            Loads and initializes background images and UI elements for login window.

        create_lobby_elements() -> None:
            Loads and initializes background images and UI elements for lobby window.

        error_window(text: str) -> tuple:
            Creates and returns error message UI elements, including text and a back button.
    """

    def __init__(self):
        self.vpn_client = None
        self.text_color = "#c6c4c3"
        self.hovering_color = "#fefac9"
        self.inactive_color = "#A9A9A9"
        self.config = load_client_settings()
        self.cursor = Cursor()

    def set_window_caption(self, title: str) -> None:
        pygame.display.set_caption(f"Tavern of Ashan - {title}")

    def play_background_music(self, music_path: str) -> None:
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(os.path.join(os.getcwd(), music_path)), -1, 0)
        pygame.mixer.Channel(0).set_volume(self.config["volume"])

    def stop_background_music(self) -> None:
        pygame.mixer.fadeout(5000)
        pygame.quit()

    def quit_game_handling(self, crsf_token: str = None, session: requests.Session = None):
        if self.vpn_client is not None:
            self.vpn_client.set_vpn_state(False)
            if crsf_token and session:
                url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict["PATH_PLAYER_OFFLINE"]}/"
                headers = {
                    "Referer": f"https://{env_dict["SERVER_URL"]}/",
                    "X-CSRFToken": crsf_token,
                    "Content-Type": "application/json",
                }
                user_data = {"nickname": self.vpn_client.user_name}
                pygame.quit()
                session.cookies.set("csrftoken", crsf_token)
                try:
                    session.post(url, json=user_data, headers=headers)
                    logger.debug("Notified server about going offline.")
                except:
                    logger.warning("Failed to notify server about going offline.")
        sys.exit()

    def create_universal_elements(self) -> None:
        self.SMALLER_WINDOW_BASE = pygame.image.load(os.path.join(os.getcwd(), "resources/frames_and_bg/player_search_frame.png"))
        self.BUTTON = pygame.image.load(os.path.join(os.getcwd(), "resources/top_bar/button_dark.png"))
        self.BUTTON_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/top_bar/button_highlighted.png"))
        self.QUIT = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/close_dark.png"))
        self.QUIT_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/close_highlighted.png"))
        self.CHECKBOX = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/iconsquare_dark.png"))
        self.CHECKBOX_CHECKED = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/selected.png"))
        self.LINE = pygame.image.load(os.path.join(os.getcwd(), "resources/frames_and_bg/separating_stripe.png"))
        self.QUESTION_MARK = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/qm1.png"))
        self.QUESTION_MARK_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/qm2.png"))

    def create_login_elements(self) -> None:
        self.create_universal_elements()
        self.LOGIN_BG = pygame.image.load(os.path.join(os.getcwd(), "resources/frames_and_bg/login_bg.png"))
        self.CHECK_MARK = pygame.image.load(os.path.join(os.getcwd(), "resources/registration/yes2.png"))
        self.CHECK_MARK_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/registration/yes1.png"))
        self.UNCHECK_MARK = pygame.image.load(os.path.join(os.getcwd(), "resources/registration/no2.png"))
        self.UNCHECK_MARK_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/registration/no1.png"))
        self.TEXT_INPUT = pygame.image.load(os.path.join(os.getcwd(), "resources/registration/registration_window.png"))
        self.TEXT_BG = pygame.image.load(os.path.join(os.getcwd(), "resources/frames_and_bg/registration_frame_2.png"))

    def create_lobby_elements(self) -> None:
        self.create_universal_elements()
        self.MAIN_BG = pygame.image.load(os.path.join(os.getcwd(), "resources/frames_and_bg/main_bg.png"))
        self.PLAYER_INFO = pygame.image.load(os.path.join(os.getcwd(), "resources/frames_and_bg/player_info.png"))
        self.PLAYER_LIST = pygame.image.load(os.path.join(os.getcwd(), "resources/players_online/players_online.png"))
        self.TOP_BAR = pygame.image.load(os.path.join(os.getcwd(), "resources/top_bar/top_bar.png"))
        self.ICON_SQUARE = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/iconsquare_dark.png"))
        self.ICON_SQUARE_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/iconsquare_highlighted.png"))
        self.OPTIONS = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/options_dark.png"))
        self.OPTIONS_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/options_highlighted.png"))
        self.CANCEL_BUTTON = pygame.image.load(os.path.join(os.getcwd(), "resources/searching_game/red_button_dark.png"))
        self.CANCEL_BUTTON_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/searching_game/red_button_highlighted.png"))
        self.CANCEL_BUTTON_INACTIVE = pygame.image.load(os.path.join(os.getcwd(), "resources/searching_game/red_button_desaturated.png"))
        self.ACCEPT_BUTTON = pygame.image.load(os.path.join(os.getcwd(), "resources/searching_game/green_button_dark.png"))
        self.ACCEPT_BUTTON_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/searching_game/green_button_highlighted.png"))
        self.ACCEPT_BUTTON_INACTIVE = pygame.image.load(os.path.join(os.getcwd(), "resources/searching_game/green_button_desaturated.png"))
        self.PROGRESS_BAR_FRAME = pygame.image.load(os.path.join(os.getcwd(), "resources/progress_bar/progress_bar_frame.png"))
        self.PROGRESS_BAR_BG = pygame.image.load(os.path.join(os.getcwd(), "resources/progress_bar/progress_bar_bg.png"))
        self.PROGRESS_BAR_EDGE = pygame.image.load(os.path.join(os.getcwd(), "resources/progress_bar/progress_bar_edge.png"))
        self.SCROLL = pygame.image.load(os.path.join(os.getcwd(), "resources/players_online/scroll.png"))
        self.SCROLL_BAR = pygame.image.load(os.path.join(os.getcwd(), "resources/players_online/scroll_bar.png"))
        self.LEFT_FRAME = pygame.image.load(os.path.join(os.getcwd(), "resources/frames_and_bg/frame.png"))
        self.HELP_FRAME = pygame.image.load(os.path.join(os.getcwd(), "resources/frames_and_bg/help_window.png"))
        self.DISCORD_LOGO = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/discord_logo.png"))
        self.DISCORD_LOGO_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/discord_logo_highlighted.png"))
        self.ARROW_LEFT = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/settings_arrow_left_dark.png"))
        self.ARROW_LEFT_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/settings_arrow_left_light.png"))
        self.ARROW_RIGHT = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/settings_arrow_right_dark.png"))
        self.ARROW_RIGHT_HIGHLIGHTED = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/settings_arrow_right_light.png"))
        self.SETTINGS_SCROLL_BAR = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/sound_settings_scroll_bar.png"))
        self.SETTINGS_SCROLL_MARKER = pygame.image.load(os.path.join(os.getcwd(), "resources/buttons/sound_settings_scroll.png"))

    def rescale_lobby_elements(self, reload: bool = False):
        if reload:
            self.create_lobby_elements()

        self.button_dims = (280, 60)
        self.top_elements_dims = (50, 50)
        self.discord_logo_dims = (60, 60)
        self.player_list_dims = (
            400 * (transformation_factors[self.transformation_option][0]),
            1000 * (transformation_factors[self.transformation_option][1]),
        )
        self.frame_dims = (
            520 * (transformation_factors[self.transformation_option][0]),
            800 * (transformation_factors[self.transformation_option][1]),
        )
        self.frame_position = (
            15 * (transformation_factors[self.transformation_option][0]),
            240 * (transformation_factors[self.transformation_option][1]),
        )
        self.option_box_dims = (
            160 * (transformation_factors[self.transformation_option][0]),
            40 * (transformation_factors[self.transformation_option][1]),
        )
        self.quit_frame_dims = (
            60 * (transformation_factors[self.transformation_option][0]),
            60 * (transformation_factors[self.transformation_option][1]),
        )
        self.checkbox_dims = (
            40 * (transformation_factors[self.transformation_option][0]),
            40 * (transformation_factors[self.transformation_option][1]),
        )
        self.settings_checkbox_dims = (
            50 * (transformation_factors[self.transformation_option][0]),
            50 * (transformation_factors[self.transformation_option][1]),
        )
        self.hoverbox_dims = (
            40 * (transformation_factors[self.transformation_option][0]),
            60 * (transformation_factors[self.transformation_option][1]),
        )
        self.arrows_dims = (
            30 * (transformation_factors[self.transformation_option][0]),
            30 * (transformation_factors[self.transformation_option][1]),
        )
        self.player_info_dims = (
            360 * (transformation_factors[self.transformation_option][0]),
            200 * (transformation_factors[self.transformation_option][1]),
        )
        self.player_icon_dims = (
            75 * (transformation_factors[self.transformation_option][0]),
            75 * (transformation_factors[self.transformation_option][1]),
        )
        self.PLAYER_LIST_FRAME = pygame.transform.scale(
            self.LEFT_FRAME,
            (
                300 * (transformation_factors[self.transformation_option][0]),
                80 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.TOP_BAR = pygame.transform.scale(
            self.TOP_BAR,
            (
                1400 * (transformation_factors[self.transformation_option][0]),
                100 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.PROGRESS_BAR_FRAME = pygame.transform.scale(
            self.PROGRESS_BAR_FRAME,
            (
                580 * (transformation_factors[self.transformation_option][0]),
                60 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.PROGRESS_BAR_BG = pygame.transform.scale(
            self.PROGRESS_BAR_BG,
            (
                500 * (transformation_factors[self.transformation_option][0]),
                30 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.PROGRESS_BAR_EDGE = pygame.transform.scale(
            self.PROGRESS_BAR_EDGE,
            (
                60 * (transformation_factors[self.transformation_option][0]),
                80 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.SCROLL = pygame.transform.scale(
            self.SCROLL,
            (
                30 * (transformation_factors[self.transformation_option][0]),
                100 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.SCROLL_BAR = pygame.transform.scale(
            self.SCROLL_BAR,
            (
                50 * (transformation_factors[self.transformation_option][0]),
                900 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.LINE = pygame.transform.scale(
            self.LINE,
            (
                330 * (transformation_factors[self.transformation_option][0]),
                5 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.PROFILE_LINE = pygame.transform.scale(
            self.LINE,
            (
                160 * (transformation_factors[self.transformation_option][0]),
                2 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.SETTINGS_SCROLL_BAR = pygame.transform.scale(
            self.SETTINGS_SCROLL_BAR,
            (
                250 * (transformation_factors[self.transformation_option][0]),
                30 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.SETTINGS_SCROLL_MARKER = pygame.transform.scale(
            self.SETTINGS_SCROLL_MARKER,
            (
                30 * (transformation_factors[self.transformation_option][0]),
                30 * (transformation_factors[self.transformation_option][1]),
            ),
        )
        self.BG = pygame.transform.scale(self.MAIN_BG, self.resolution)
        self.PLAYER_LIST = pygame.transform.scale(self.PLAYER_LIST, self.player_list_dims)
        self.PLAYER_INFO = pygame.transform.scale(self.PLAYER_INFO, self.player_info_dims)
        self.PLAYER_LIST_BG = pygame.Surface(self.player_list_dims, pygame.SRCALPHA)
        self.OPTIONS = pygame.transform.scale(self.OPTIONS, self.top_elements_dims)
        self.OPTIONS_HIGHLIGHTED = pygame.transform.scale(self.OPTIONS_HIGHLIGHTED, self.top_elements_dims)
        self.ICON_SQUARE = pygame.transform.scale(self.ICON_SQUARE, self.player_icon_dims)
        self.ICON_SQUARE_HIGHLIGHTED = pygame.transform.scale(self.ICON_SQUARE_HIGHLIGHTED, self.player_icon_dims)
        self.QUIT_LOBBY = pygame.transform.scale(self.QUIT, self.top_elements_dims)
        self.QUIT_LOBBY_HIGHLIGHTED = pygame.transform.scale(self.QUIT_HIGHLIGHTED, self.top_elements_dims)
        self.QUIT_FRAME = pygame.transform.scale(self.QUIT, self.quit_frame_dims)
        self.QUIT_FRAME_HIGHLIGHTED = pygame.transform.scale(self.QUIT_HIGHLIGHTED, self.quit_frame_dims)
        self.BUTTON = pygame.transform.scale(self.BUTTON, self.button_dims)
        self.BUTTON_HIGHLIGHTED = pygame.transform.scale(self.BUTTON_HIGHLIGHTED, self.button_dims)
        self.ACCEPT_BUTTON = pygame.transform.scale(self.ACCEPT_BUTTON, self.button_dims)
        self.ACCEPT_BUTTON_HIGHLIGHTED = pygame.transform.scale(self.ACCEPT_BUTTON_HIGHLIGHTED, self.button_dims)
        self.ACCEPT_BUTTON_INACTIVE = pygame.transform.scale(self.ACCEPT_BUTTON_INACTIVE, self.button_dims)
        self.CANCEL_BUTTON = pygame.transform.scale(self.CANCEL_BUTTON, self.button_dims)
        self.CANCEL_BUTTON_HIGHLIGHTED = pygame.transform.scale(self.CANCEL_BUTTON_HIGHLIGHTED, self.button_dims)
        self.CANCEL_BUTTON_INACTIVE = pygame.transform.scale(self.CANCEL_BUTTON_INACTIVE, self.button_dims)
        self.CHECKBOX = pygame.transform.scale(self.CHECKBOX, self.checkbox_dims)
        self.CHECKBOX_CHECKED = pygame.transform.scale(self.CHECKBOX_CHECKED, self.checkbox_dims)
        self.CHECKBOX_SETTINGS = pygame.transform.scale(self.CHECKBOX, self.settings_checkbox_dims)
        self.CHECKBOX_SETTINGS_CHECKED = pygame.transform.scale(self.CHECKBOX_CHECKED, self.settings_checkbox_dims)
        self.QUESTION_MARK = pygame.transform.scale(self.QUESTION_MARK, self.hoverbox_dims)
        self.QUESTION_MARK_HIGHLIGHTED = pygame.transform.scale(self.QUESTION_MARK_HIGHLIGHTED, self.hoverbox_dims)
        self.LEFT_FRAME = pygame.transform.scale(self.LEFT_FRAME, self.frame_dims)
        self.DISCORD_LOGO = pygame.transform.scale(self.DISCORD_LOGO, self.discord_logo_dims)
        self.DISCORD_LOGO_HIGHLIGHTED = pygame.transform.scale(self.DISCORD_LOGO_HIGHLIGHTED, self.discord_logo_dims)
        self.NARROW_LINE = pygame.transform.scale(self.LINE, (self.frame_dims[0] * 0.8, 3))
        self.WIDE_LINE = pygame.transform.scale(self.LINE, (self.frame_dims[0] * 0.8, 5))
        self.ARROW_LEFT = pygame.transform.scale(self.ARROW_LEFT, self.arrows_dims)
        self.ARROW_LEFT_HIGHLIGHTED = pygame.transform.scale(self.ARROW_LEFT_HIGHLIGHTED, self.arrows_dims)
        self.ARROW_RIGHT = pygame.transform.scale(self.ARROW_RIGHT, self.arrows_dims)
        self.ARROW_RIGHT_HIGHLIGHTED = pygame.transform.scale(self.ARROW_RIGHT_HIGHLIGHTED, self.arrows_dims)

    def error_window(self, text: str, dimensions: tuple[int, int], button_text: str = "Back") -> tuple:
        overlay_width, overlay_height = dimensions
        screen_width, screen_height = pygame.display.get_surface().get_size()
        overlay_y = (screen_height - overlay_height) // 2

        self.SMALLER_WINDOWS_BG = pygame.transform.scale(self.SMALLER_WINDOW_BASE, (overlay_width, overlay_height))

        WRONG_PASSWORD_TEXT = render_small_caps(text, int(self.font_size[0]), self.text_color)
        WRONG_PASSOWRD_RECT = WRONG_PASSWORD_TEXT.get_rect(center=(screen_width // 2, overlay_y + overlay_height // 3))

        BACK_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(screen_width // 2, overlay_y + overlay_height * 2 // 3),
            text_input=button_text,
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )

        return (WRONG_PASSWORD_TEXT, WRONG_PASSOWRD_RECT, BACK_BUTTON)
