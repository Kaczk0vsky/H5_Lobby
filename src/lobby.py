import pygame
import os
import toml
import time
import requests
import random
import ctypes

from pygame.locals import *

from src.global_vars import (
    resolution_choices,
    transformation_factors,
    fonts_sizes,
    bg_sound_volume,
    env_dict,
)
from src.basic_window import BasicWindow
from src.run_ashan_arena import AschanArena3Game
from src.helpers import play_on_empty, calculate_time_passed, get_window
from src.custom_thread import CustomThread
from src.decorators import run_in_thread
from widgets.button import Button
from widgets.option_box import OptionBox
from widgets.progress_bar import ProgressBar


class H5_Lobby(BasicWindow):
    """
    The H5_Lobby class represents the main menu and lobby system for the game.
    It provides a graphical user interface (GUI) for players to navigate
    through various options, including finding a game, viewing statistics,
    accessing news, managing their profile, and adjusting game settings.

    Methods:
        main_menu():
            Displays the main menu and handles button interactions, including
            game queueing and accessing submenus.

        queue_window():
            Displays the matchmaking queue interface, handling the process of
            finding an opponent and accepting a match.

        options_window():
            Displays the settings menu, allowing the player to adjust screen
            resolution and apply changes.

        run_game():
            Starts the lobby system by initializing and displaying the main menu.
    """

    _error_status = False
    _queue_canceled = False
    _window_overlay = False
    _game_found_music = False
    _get_time = False
    _found_game = False
    _opponent_accepted = False
    _authentication_error = False
    _opponent_declined = False
    _player_accepted = False
    _queue_status = False
    _error_status = False
    _window_overlay = False
    _update_queue_status = False
    _elapsed_time = None
    _queue_channel = None
    _opponent_nickname = ""

    def __init__(
        self,
        vpn_client: object,
        client_config: dict,
        crsf_token: str,
        session: requests.Session,
    ):
        BasicWindow.__init__(self)

        self.vpn_client = vpn_client
        self.client_config = client_config
        self.crsf_token = crsf_token
        self.session = session
        self.transformation_option = (
            f"{self.config["screen_width"]}x{self.config["screen_hight"]}"
        )
        self.font_size = fonts_sizes[self.transformation_option]

        self.set_window_caption(title="Menu")
        self.play_background_music(music_path="resources/H5_main_theme.mp3")
        self.create_lobby_elements()

        self.SCREEN = pygame.display.set_mode(
            (self.config["screen_width"], self.config["screen_hight"]), pygame.RESIZABLE
        )

    def main_menu(self):
        def set_queue_vars(state: bool = False) -> None:
            self._game_found_music = state
            self._get_time = state
            self._found_game = state
            self._opponent_accepted = state
            self._player_accepted = state
            self._queue_status = state
            self._elapsed_time = None
            self._queue_channel = None
            self._opponent_nickname = ""

        def set_all_buttons_active(is_active: bool = False) -> None:
            FIND_GAME_BUTTON.set_active(is_active)
            VIEW_STATISTICS.set_active(is_active)
            NEWS.set_active(is_active)
            MY_PROFILE.set_active(is_active)
            # OPTIONS_BUTTON.set_active(is_active)

        self.button_dims = (
            self.config["screen_width"] / 9,
            self.config["screen_hight"] / 17,
        )
        self.top_elements_dims = (
            self.config["screen_width"] / 28,
            self.config["screen_hight"] / 17,
        )

        self.BG = pygame.transform.scale(
            self.BG,
            (self.config["screen_width"], self.config["screen_hight"]),
        )
        self.TOP_BAR = pygame.transform.scale(
            self.TOP_BAR,
            (self.config["screen_width"] / 1.5, self.config["screen_hight"] / 10),
        )
        self.PLAYER_LIST = pygame.transform.scale(
            self.PLAYER_LIST,
            (self.config["screen_width"] / 5, self.config["screen_hight"] / 1.5),
        )
        self.PLAYER_LIST_BG = pygame.Surface(
            (
                350 * (transformation_factors[self.transformation_option][0]),
                680 * (transformation_factors[self.transformation_option][1]),
            ),
            pygame.SRCALPHA,
        )
        self.PLAYER_LIST_BG.fill((0, 0, 0, 200))
        self.PLAYERS_TEXT = self.get_font(self.font_size[0]).render(
            "Players active", True, self.text_color
        )
        self.PLAYERS_TEXT_RECT = self.PLAYERS_TEXT.get_rect(
            center=(
                1730 * (transformation_factors[self.transformation_option][0]),
                180 * transformation_factors[self.transformation_option][1],
            ),
        )
        self.NEWS = pygame.transform.scale(
            self.NEWS,
            (self.config["screen_width"] / 2, self.config["screen_hight"] / 1.5),
        )
        self.OPTIONS = pygame.transform.scale(
            self.OPTIONS,
            self.top_elements_dims,
        )
        self.OPTIONS_HIGHLIGHTED = pygame.transform.scale(
            self.OPTIONS_HIGHLIGHTED,
            self.top_elements_dims,
        )
        self.ICON_SQUARE = pygame.transform.scale(
            self.ICON_SQUARE,
            self.top_elements_dims,
        )
        self.ICON_SQUARE_HIGHLIGHTED = pygame.transform.scale(
            self.ICON_SQUARE_HIGHLIGHTED,
            self.top_elements_dims,
        )
        self.QUIT = pygame.transform.scale(
            self.QUIT,
            self.top_elements_dims,
        )
        self.QUIT_HIGHLIGHTED = pygame.transform.scale(
            self.QUIT_HIGHLIGHTED,
            self.top_elements_dims,
        )
        self.BUTTON = pygame.transform.scale(
            self.BUTTON,
            self.button_dims,
        )
        self.BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.BUTTON_HIGHLIGHTED,
            self.button_dims,
        )
        self.ACCEPT_BUTTON = pygame.transform.scale(
            self.ACCEPT_BUTTON,
            self.button_dims,
        )
        self.ACCEPT_BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.ACCEPT_BUTTON_HIGHLIGHTED,
            self.button_dims,
        )
        self.ACCEPT_BUTTON_INACTIVE = pygame.transform.scale(
            self.ACCEPT_BUTTON_INACTIVE,
            self.button_dims,
        )
        self.CANCEL_BUTTON = pygame.transform.scale(
            self.CANCEL_BUTTON,
            self.button_dims,
        )
        self.CANCEL_BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.CANCEL_BUTTON_HIGHLIGHTED,
            self.button_dims,
        )
        self.CANCEL_BUTTON_INACTIVE = pygame.transform.scale(
            self.CANCEL_BUTTON_INACTIVE,
            self.button_dims,
        )
        self.PROGRESS_BAR_FRAME = pygame.transform.scale(
            self.PROGRESS_BAR_FRAME,
            (580, 60),
        )
        self.PROGRESS_BAR_BG = pygame.transform.scale(
            self.PROGRESS_BAR_BG,
            (500, 30),
        )
        self.PROGRESS_BAR_EDGE = pygame.transform.scale(
            self.PROGRESS_BAR_EDGE,
            (60, 80),
        )
        FIND_GAME_BUTTON = Button(
            image=self.CANCEL_BUTTON,
            image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
            image_inactive=self.CANCEL_BUTTON_INACTIVE,
            position=(
                830 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            text_input="Find Game",
            font=self.get_font(self.font_size[1]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )
        VIEW_STATISTICS = Button(
            image=self.CANCEL_BUTTON,
            image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
            image_inactive=self.CANCEL_BUTTON_INACTIVE,
            position=(
                1080 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            text_input="View Statistics",
            font=self.get_font(self.font_size[1]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )
        NEWS = Button(
            image=self.CANCEL_BUTTON,
            image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
            image_inactive=self.CANCEL_BUTTON_INACTIVE,
            position=(
                1330 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            text_input="News",
            font=self.get_font(self.font_size[1]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )
        MY_PROFILE = Button(
            image=self.CANCEL_BUTTON,
            image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
            image_inactive=self.CANCEL_BUTTON_INACTIVE,
            position=(
                1580 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            text_input="My Account",
            font=self.get_font(self.font_size[1]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )
        PLAYER_PROFILE = Button(
            image=self.ICON_SQUARE,
            image_highlited=self.ICON_SQUARE_HIGHLIGHTED,
            position=(
                1730 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            font=self.get_font(self.font_size[1]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        OPTIONS_BUTTON = Button(
            image=self.OPTIONS,
            image_highlited=self.OPTIONS_HIGHLIGHTED,
            position=(
                1800 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            font=self.get_font(self.font_size[1]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        QUIT_BUTTON = Button(
            image=self.QUIT,
            image_highlited=self.QUIT_HIGHLIGHTED,
            position=(
                1870 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            font=self.get_font(self.font_size[1]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            self.cursor.update()
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            self.SCREEN.blit(
                self.TOP_BAR,
                (
                    635 * (transformation_factors[self.transformation_option][0]),
                    5 * (transformation_factors[self.transformation_option][1]),
                ),
            )
            self.SCREEN.blit(
                self.PLAYER_LIST_BG,
                (
                    1550 * (transformation_factors[self.transformation_option][0]),
                    120 * (transformation_factors[self.transformation_option][1]),
                ),
            )
            self.SCREEN.blit(
                self.PLAYER_LIST,
                (
                    1530 * (transformation_factors[self.transformation_option][0]),
                    100 * (transformation_factors[self.transformation_option][1]),
                ),
            )
            self.SCREEN.blit(self.PLAYERS_TEXT, self.PLAYERS_TEXT_RECT)

            # TODO: add news block
            # self.SCREEN.blit(
            #     self.NEWS,
            #     (
            #         550 * (transformation_factors[self.transformation_option][0]),
            #         100 * (transformation_factors[self.transformation_option][1]),
            #     ),
            # )

            for button in [
                FIND_GAME_BUTTON,
                VIEW_STATISTICS,
                NEWS,
                MY_PROFILE,
                PLAYER_PROFILE,
                OPTIONS_BUTTON,
                QUIT_BUTTON,
            ]:
                button.handle_button(self.SCREEN, MENU_MOUSE_POS)

            if self._queue_status:
                if self._update_queue_status:
                    (
                        CANCEL_QUEUE,
                        ACCEPT_QUEUE,
                        OPONNENT_TEXT,
                        OPONNENT_RECT,
                        PROGRESS_BAR,
                    ) = self.queue_window()
                    ACCEPT_QUEUE.set_active(False) if self._player_accepted else None
                    self._update_queue_status = False

                self.SCREEN.blit(
                    self.SMALLER_WINDOWS_BG,
                    (
                        640 * transformation_factors[self.transformation_option][0],
                        360 * transformation_factors[self.transformation_option][1],
                    ),
                )

                CANCEL_QUEUE.handle_button(self.SCREEN, MENU_MOUSE_POS)
                if ACCEPT_QUEUE is not None:
                    ACCEPT_QUEUE.handle_button(self.SCREEN, MENU_MOUSE_POS)
                if not self._found_game:
                    minutes, seconds = calculate_time_passed(self.start_time)
                    HEADER_TEXT = self.get_font(self.font_size[0]).render(
                        f"Waiting for opponent: {minutes}:{seconds:02d}",
                        True,
                        self.text_color,
                    )
                    HEADER_RECT = HEADER_TEXT.get_rect(
                        center=(
                            self.SCREEN.get_width() / 2,
                            self.SCREEN.get_height() / 2.4,
                        )
                    )
                else:
                    HEADER_TEXT = self.get_font(self.font_size[0]).render(
                        "GAME FOUND", True, self.text_color
                    )
                    HEADER_RECT = HEADER_TEXT.get_rect(
                        center=(
                            self.SCREEN.get_width() / 2,
                            self.SCREEN.get_height() / 2.4,
                        )
                    )
                self.SCREEN.blit(HEADER_TEXT, HEADER_RECT)
                if OPONNENT_TEXT is not None and OPONNENT_RECT is not None:
                    self.SCREEN.blit(OPONNENT_TEXT, OPONNENT_RECT)
                if PROGRESS_BAR is not None and not self._player_accepted:
                    cancel_bar = PROGRESS_BAR.draw(self.SCREEN, self._elapsed_time)
                    if cancel_bar:
                        self._queue_canceled = True
                        self._error_status = True
                        self._window_overlay = True
                        pygame.mixer.Channel(0).set_volume(bg_sound_volume)
                        pygame.mixer.Channel(self._queue_channel).stop()
                        set_queue_vars(state=False)
                        set_all_buttons_active(True)
                        self.remove_from_queue(is_accepted=False)
                        continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game_handling(self.crsf_token, self.session)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if FIND_GAME_BUTTON.check_for_input(MENU_MOUSE_POS):
                        self._update_queue_status = True
                        self._queue_status = True
                        set_all_buttons_active(is_active=False)
                        self.add_to_queue()
                        continue
                    if VIEW_STATISTICS.check_for_input(MENU_MOUSE_POS):
                        pass
                    if NEWS.check_for_input(MENU_MOUSE_POS):
                        pass
                    if MY_PROFILE.check_for_input(MENU_MOUSE_POS):
                        pass
                    if PLAYER_PROFILE.check_for_input(MENU_MOUSE_POS):
                        pass
                    if OPTIONS_BUTTON.check_for_input(MENU_MOUSE_POS):
                        self.options_window()
                    if QUIT_BUTTON.check_for_input(MENU_MOUSE_POS):
                        self.quit_game_handling(self.crsf_token, self.session)
                    if self._queue_status:
                        if CANCEL_QUEUE.check_for_input(MENU_MOUSE_POS):
                            set_all_buttons_active(is_active=True)
                            pygame.mixer.Channel(0).set_volume(bg_sound_volume)
                            if self._queue_channel:
                                pygame.mixer.Channel(self._queue_channel).stop()
                            set_queue_vars(state=False)
                            self.remove_from_queue(is_accepted=False)
                        if ACCEPT_QUEUE is not None:
                            if ACCEPT_QUEUE.check_for_input(MENU_MOUSE_POS):
                                self._update_queue_status = True
                                self._player_accepted = True
                                set_all_buttons_active(is_active=False)
                                self.remove_from_queue(is_accepted=True)
                                self.check_if_oponnent_accepted()

                    if self._window_overlay:
                        if self._error_status:
                            if RETURN_BUTTON.check_for_input(MENU_MOUSE_POS):
                                if self._queue_canceled:
                                    self._queue_canceled = False
                                elif self._authentication_error:
                                    self._authentication_error = False
                                self._window_overlay = False
                                self._error_status = False

            if self._opponent_accepted and self._player_accepted:
                pygame.mixer.Channel(self._queue_channel).stop()
                set_queue_vars(state=False)
                set_all_buttons_active(is_active=True)
                self.run_arena()

            if self._opponent_declined:
                self._update_queue_status = True
                self._opponent_declined = False
                self._found_game = False
                self._player_accepted = False
                self._game_found_music = False
                self._elapsed_time = None
                pygame.mixer.Channel(0).set_volume(bg_sound_volume)
                if self._queue_channel:
                    pygame.mixer.Channel(self._queue_channel).stop()
                self.add_to_queue()

            if self._queue_canceled:
                error_text = "Queue has been declined"

            if self._authentication_error:
                error_text = "CRSF Token is not valid"

            if self._error_status:
                (WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT, RETURN_BUTTON) = (
                    self.error_window(text=error_text)
                )
                screen_width, screen_height = (
                    self.SCREEN.get_width(),
                    self.SCREEN.get_height(),
                )
                window_width, window_height = (
                    self.SMALLER_WINDOWS_BG.get_width(),
                    self.SMALLER_WINDOWS_BG.get_height(),
                )

                x_position = (screen_width - window_width) // 2
                y_position = (screen_height - window_height) // 2

                self.SCREEN.blit(self.SMALLER_WINDOWS_BG, (x_position, y_position))
                self.SCREEN.blit(WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT)
                RETURN_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)

            pygame.display.update()

    def queue_window(self):
        overlay_width, overlay_height = (
            self.config["screen_width"] // 3,
            self.config["screen_hight"] // 3,
        )
        self.SMALLER_WINDOWS_BG = pygame.transform.scale(
            self.SMALLER_WINDOWS_BG, (overlay_width, overlay_height)
        )

        if not self._get_time:
            self.start_time = time.time()
            self._get_time = True

        CANCEL_BUTTON = Button(
            image=self.CANCEL_BUTTON,
            image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
            position=(overlay_width * 1.5, overlay_height * 1.8),
            text_input="Cancel",
            font=self.get_font(self.font_size[1]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )

        ACCEPT_BUTTON = None
        OPONNENT_TEXT = None
        OPONNENT_RECT = None
        PROGRESS_BAR = None

        if self._found_game:
            if not self._elapsed_time:
                self._elapsed_time = time.time()
            if not self._game_found_music:
                self._queue_channel = play_on_empty(
                    "resources/match_found.mp3", volume=bg_sound_volume
                )
                pygame.mixer.Channel(0).set_volume(0.0)
                self._game_found_music = True

            if self._player_accepted:
                information_str = f"Waiting for {self._opponent_nickname} to accept..."
            else:
                information_str = (
                    f"{self._opponent_nickname} - {self.oponnent_ranking_points} RP"
                )
            OPONNENT_TEXT = self.get_font(self.font_size[0]).render(
                information_str,
                True,
                self.text_color,
            )
            OPONNENT_RECT = OPONNENT_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() / 2.12,
                )
            )
            ACCEPT_BUTTON = Button(
                image=self.ACCEPT_BUTTON,
                image_highlited=self.ACCEPT_BUTTON_HIGHLIGHTED,
                image_inactive=self.ACCEPT_BUTTON_INACTIVE,
                pos=(overlay_width * 1.3, overlay_height * 1.8),
                text_input="Accept",
                font=self.get_font(self.font_size[1]),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
                inactive_color=self.inactive_color,
            )
            CANCEL_BUTTON = Button(
                image=self.CANCEL_BUTTON,
                image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
                image_inactive=self.CANCEL_BUTTON_INACTIVE,
                pos=(overlay_width * 1.7, overlay_height * 1.8),
                text_input="Cancel",
                font=self.get_font(self.font_size[1]),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
                inactive_color=self.inactive_color,
            )
            if not self._player_accepted:
                PROGRESS_BAR = ProgressBar(
                    position=(overlay_width * 1.5, overlay_height * 1.6),
                    dimensions=(overlay_width * 0.8, 30),
                    image_frame=self.PROGRESS_BAR_FRAME,
                    image_bg=self.PROGRESS_BAR_BG,
                    image_edge=self.PROGRESS_BAR_EDGE,
                )

        return (
            CANCEL_BUTTON,
            ACCEPT_BUTTON,
            OPONNENT_TEXT,
            OPONNENT_RECT,
            PROGRESS_BAR,
        )

    def options_window(self):
        RESOLUTION_TEXT = self.get_font(self.font_size[1]).render(
            "Select resolution", True, "#d7fcd4"
        )
        RESOLUTION_RECT = RESOLUTION_TEXT.get_rect(
            center=(
                130 * (transformation_factors[self.transformation_option][0]),
                300 * transformation_factors[self.transformation_option][1],
            ),
        )
        BACK_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            pos=(
                290 * (transformation_factors[self.transformation_option][0]),
                800 * (transformation_factors[self.transformation_option][1]),
            ),
            text_input="Back",
            font=self.get_font(self.font_size[1]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        RESOLUTION_CHOICES = OptionBox(
            position=(
                (self.SCREEN.get_width() / 6.5),
                (self.SCREEN.get_height() / 3.9),
            ),
            dimensions=(160, 40),
            color=pygame.Color("gray"),
            highlight_color=pygame.Color("deepskyblue"),
            font=pygame.font.SysFont(None, 30),
            option_list=resolution_choices,
            selected=resolution_choices.index(self.transformation_option),
        )

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            self.cursor.update()
            OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

            self.SCREEN.blit(RESOLUTION_TEXT, RESOLUTION_RECT)

            BACK_BUTTON.handle_button(self.SCREEN, OPTIONS_MOUSE_POS)

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    self.quit_game_handling(self.crsf_token, self.session)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.check_for_input(OPTIONS_MOUSE_POS):
                        self.main_menu()

            selected_option = RESOLUTION_CHOICES.update(event_list)
            if selected_option != None:
                resolution = resolution_choices[selected_option]
                if "fullscreen" in resolution.lower():
                    monitor_resolution = pygame.display.Info()
                    self.SCREEN = pygame.display.set_mode(
                        (monitor_resolution.current_w, monitor_resolution.current_h),
                        pygame.FULLSCREEN,
                    )
                else:
                    self.transformation_option = resolution
                    resolutions = resolution.split("x")
                    self.config["screen_width"] = int(resolutions[0])
                    self.config["screen_hight"] = int(resolutions[1])
                    self.SCREEN = pygame.display.set_mode(
                        (self.config["screen_width"], self.config["screen_hight"])
                    )
                    self.BG = pygame.image.load(
                        os.path.join(os.getcwd(), "resources/h5_background.jpg")
                    )
                    self.BG = pygame.transform.scale(
                        self.BG,
                        (self.config["screen_width"], self.config["screen_hight"]),
                    )

                with open(os.path.join(os.getcwd(), "settings.toml"), "r") as f:
                    data = toml.load(f)
                    data["resolution"] = self.config

                with open(os.path.join(os.getcwd(), "settings.toml"), "w") as f:
                    toml.dump(data, f)

            RESOLUTION_CHOICES.draw(
                self.SCREEN,
                300 * (transformation_factors[self.transformation_option][0]),
                280 * (transformation_factors[self.transformation_option][1]),
                160,
                40,
            )
            pygame.display.update()

    def add_to_queue(self):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict["PATH_ADD"]}/"
        if not self.crsf_token:
            self._window_overlay = True
            self._authentication_error = True
            self._error_status = True
            return

        user_data = {"nickname": self.client_config["nickname"]}
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }
        response = self.session.post(url, json=user_data, headers=headers)

        if response.status_code == 200:
            self.check_queue = CustomThread(target=self.scan_for_players, daemon=True)
            self.check_queue.start()

    def remove_from_queue(self, is_accepted: bool):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict["PATH_REMOVE"]}/"
        if not self.crsf_token:
            self._window_overlay = True
            self._authentication_error = True
            self._error_status = True
            return

        user_data = {
            "nickname": self.client_config["nickname"],
            "is_accepted": is_accepted,
        }
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }

        self.session.post(url, json=user_data, headers=headers)

    def scan_for_players(self):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict["PATH_GET_PLAYERS"]}/"
        if not self.crsf_token:
            self._window_overlay = True
            self._authentication_error = True
            self._error_status = True
            return

        user_data = {"nickname": self.client_config["nickname"]}
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }

        while True:
            try:
                response = self.session.post(url, json=user_data, headers=headers)
                if response.status_code == 200:
                    json_response = response.json()
                    if json_response.get("game_found"):
                        self._update_queue_status = True
                        self._found_game = True
                        self._opponent_nickname = json_response.get("opponent")[0]
                        self.oponnent_ranking_points = json_response.get("opponent")[1]
                        break

            except Exception as e:
                pass

            time.sleep(random.randint(1, 5))

    @run_in_thread
    def check_if_oponnent_accepted(self):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict['PATH_CHECK_OPONNENT']}/"
        if not self.crsf_token:
            self._window_overlay = True
            self._authentication_error = True
            self._error_status = True
            return

        user_data = {"nickname": self.client_config["nickname"]}
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }

        while True:
            try:
                response = self.session.post(url, json=user_data, headers=headers)
                if response.status_code == 200:
                    json_response = response.json()
                    if json_response.get("oponnent_accepted"):
                        self._opponent_accepted = True
                        break
                    elif json_response.get("oponnent_declined"):
                        self._opponent_declined = True
                        break

            except Exception as e:
                pass

            time.sleep(1)

    def minimize_to_tray(self):
        time.sleep(0.1)
        self.window = get_window()
        self.window.minimize()
        self.window.hide()
        pygame.display.iconify()

    def maximize_from_tray(self):
        # TODO: window blinks on white, upper part is white instead of blue
        self.window.restore()
        hwnd = self.window._hWnd
        ctypes.windll.user32.ShowWindow(hwnd, 9)
        foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
        current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        foreground_thread_id = ctypes.windll.user32.GetWindowThreadProcessId(
            foreground_hwnd, 0
        )
        if foreground_thread_id != current_thread_id:
            ctypes.windll.user32.AttachThreadInput(
                current_thread_id, foreground_thread_id, True
            )
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.BringWindowToTop(hwnd)
        if foreground_thread_id != current_thread_id:
            ctypes.windll.user32.AttachThreadInput(
                current_thread_id, foreground_thread_id, False
            )
        self.play_background_music(music_path="resources/H5_main_theme.mp3")

    def run_game(self):
        self.main_menu()

    def run_arena(self):
        game = AschanArena3Game(self)
        game.run_processes()
