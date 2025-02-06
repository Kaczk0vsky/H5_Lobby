import pygame
import sys
import os
import toml
import requests
import time

from pygame.locals import *

from src.settings_reader import load_resolution_settings
from src.global_vars import (
    resolution_choices,
    transformation_factors,
    fonts_sizes,
    bg_sound_volume,
)
from src.run_ashan_arena import AschanArena3_Game
from src.helpers import play_on_empty
from window_elements.button import Button
from window_elements.option_box import OptionBox


class H5_Lobby:
    _queue_status = False
    _player_found = False
    _game_accepted = False

    def __init__(self, vpn_client):
        pygame.init()
        pygame.display.set_caption("Heroes V of Might and Magic Ashan Arena 3 - Menu")
        pygame.mixer.init()
        pygame.mixer.Channel(0).play(
            pygame.mixer.Sound(
                os.path.join(os.getcwd(), "resources/H5_main_theme.mp3")
            ),
            -1,
            0,
        )
        pygame.mixer.Channel(0).set_volume(bg_sound_volume)
        self.opponent_str = ""
        self.vpn_client = vpn_client

        self.config = load_resolution_settings()
        self.transformation_option = (
            f"{self.config["screen_width"]}x{self.config["screen_hight"]}"
        )
        self.font_size = fonts_sizes[self.transformation_option]

        self.SCREEN = pygame.display.set_mode(
            (self.config["screen_width"], self.config["screen_hight"]), pygame.RESIZABLE
        )
        self.BG = pygame.image.load(
            os.path.join(os.getcwd(), "resources/background/background.png")
        )
        self.PLAYER_LIST = pygame.image.load(
            os.path.join(os.getcwd(), "resources/background/players_online.png")
        )
        self.TOP_BAR = pygame.image.load(
            os.path.join(os.getcwd(), "resources/main_menu/top_bar.png")
        )
        self.QUEUE_BG = pygame.image.load(
            os.path.join(os.getcwd(), "resources/game_search/game_search_window.png")
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
            os.path.join(os.getcwd(), "resources/buttons/iconsquare_highlighted.png")
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

    def get_font(self, font_size: int = 75):
        return pygame.font.Font("resources/Quivira.otf", font_size)

    def main_menu(self):
        get_time = False
        refresh_queue_window = False
        found_game = False  # TODO: remove, only for testing
        is_playing = False
        queue_channel = 0

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
            "Players active", True, "#d7fcd4"
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
            (self.config["screen_width"] / 28, self.config["screen_hight"] / 17),
        )
        self.OPTIONS_HIGHLIGHTED = pygame.transform.scale(
            self.OPTIONS_HIGHLIGHTED,
            (self.config["screen_width"] / 28, self.config["screen_hight"] / 17),
        )
        self.ICON_SQUARE = pygame.transform.scale(
            self.ICON_SQUARE,
            (self.config["screen_width"] / 28, self.config["screen_hight"] / 17),
        )
        self.ICON_SQUARE_HIGHLIGHTED = pygame.transform.scale(
            self.ICON_SQUARE_HIGHLIGHTED,
            (self.config["screen_width"] / 28, self.config["screen_hight"] / 17),
        )
        self.QUIT = pygame.transform.scale(
            self.QUIT,
            (self.config["screen_width"] / 28, self.config["screen_hight"] / 17),
        )
        self.QUIT_HIGHLIGHTED = pygame.transform.scale(
            self.QUIT_HIGHLIGHTED,
            (self.config["screen_width"] / 28, self.config["screen_hight"] / 17),
        )
        self.BUTTON = pygame.transform.scale(
            self.BUTTON,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )
        self.BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.BUTTON_HIGHLIGHTED,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )
        self.ACCEPT_BUTTON = pygame.transform.scale(
            self.ACCEPT_BUTTON,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )
        self.ACCEPT_BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.ACCEPT_BUTTON_HIGHLIGHTED,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )
        self.CANCEL_BUTTON = pygame.transform.scale(
            self.CANCEL_BUTTON,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )
        self.CANCEL_BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.CANCEL_BUTTON_HIGHLIGHTED,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )

        (
            queue_window,
            CANCEL_QUEUE,
            ACCEPT_QUEUE,
            HEADER_TEXT,
            HEADER_RECT,
            OPONNENT_TEXT,
            OPONNENT_RECT,
        ) = self.queue_window()
        queue_window_x = (self.config["screen_width"] - queue_window.get_width()) // 2
        queue_window_y = (self.config["screen_hight"] - queue_window.get_height()) // 2

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
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
            # self.SCREEN.blit(
            #     self.NEWS,
            #     (
            #         550 * (transformation_factors[self.transformation_option][0]),
            #         100 * (transformation_factors[self.transformation_option][1]),
            #     ),
            # )

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            FIND_GAME_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    830 * (transformation_factors[self.transformation_option][0]),
                    50 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="Find Game",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            VIEW_STATISTICS = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    1080 * (transformation_factors[self.transformation_option][0]),
                    50 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="View Statistics",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            NEWS = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    1330 * (transformation_factors[self.transformation_option][0]),
                    50 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="News",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            MY_PROFILE = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    1580 * (transformation_factors[self.transformation_option][0]),
                    50 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="My Account",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            PLAYER_PROFILE = Button(
                image=self.ICON_SQUARE,
                image_highlited=self.ICON_SQUARE_HIGHLIGHTED,
                pos=(
                    1730 * (transformation_factors[self.transformation_option][0]),
                    50 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            OPTIONS_BUTTON = Button(
                image=self.OPTIONS,
                image_highlited=self.OPTIONS_HIGHLIGHTED,
                pos=(
                    1800 * (transformation_factors[self.transformation_option][0]),
                    50 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            QUIT_BUTTON = Button(
                image=self.QUIT,
                image_highlited=self.QUIT_HIGHLIGHTED,
                pos=(
                    1870 * (transformation_factors[self.transformation_option][0]),
                    50 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            for button in [
                FIND_GAME_BUTTON,
                VIEW_STATISTICS,
                NEWS,
                MY_PROFILE,
                PLAYER_PROFILE,
                OPTIONS_BUTTON,
                QUIT_BUTTON,
            ]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.SCREEN, MENU_MOUSE_POS)

            if self._queue_status:
                if refresh_queue_window:
                    (
                        queue_window,
                        CANCEL_QUEUE,
                        ACCEPT_QUEUE,
                        HEADER_TEXT,
                        HEADER_RECT,
                        OPONNENT_TEXT,
                        OPONNENT_RECT,
                    ) = self.queue_window()
                    refresh_queue_window = False

                if not get_time:
                    self.start_time = time.time()
                    get_time = True
                elapsed_time = round(time.time() - self.start_time)
                minutes = elapsed_time // 60
                seconds = elapsed_time % 60

                if not found_game:
                    HEADER_TEXT = self.get_font(self.font_size[0]).render(
                        f"Waiting for opponent: {minutes}:{seconds:02d}",
                        True,
                        "white",
                    )
                    HEADER_RECT = HEADER_TEXT.get_rect(
                        center=(
                            self.SCREEN.get_width() / 2,
                            self.SCREEN.get_height() / 2.4,
                        )
                    )

                # TODO: remove this if statment - ONLY FOR TESTING
                if seconds == 3:
                    found_game = True
                    self._player_found = True

                if self._player_found:
                    refresh_queue_window = True
                    if not is_playing:
                        queue_channel = play_on_empty(
                            "resources/match_found.wav", volume=bg_sound_volume
                        )
                        pygame.mixer.Channel(0).set_volume(0.0)
                        is_playing = True

                self.SCREEN.blit(self.QUEUE_BG, (queue_window_x, queue_window_y))
                self.SCREEN.blit(HEADER_TEXT, HEADER_RECT)

                CANCEL_QUEUE.changeColor(MENU_MOUSE_POS)
                CANCEL_QUEUE.update(self.SCREEN, MENU_MOUSE_POS)
                if ACCEPT_QUEUE is not None:
                    ACCEPT_QUEUE.changeColor(MENU_MOUSE_POS)
                    ACCEPT_QUEUE.update(self.SCREEN, MENU_MOUSE_POS)
                if HEADER_TEXT is not None and HEADER_RECT is not None:
                    self.SCREEN.blit(HEADER_TEXT, HEADER_RECT)
                if OPONNENT_TEXT is not None and OPONNENT_RECT is not None:
                    self.SCREEN.blit(OPONNENT_TEXT, OPONNENT_RECT)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if FIND_GAME_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self._queue_status = True
                    if VIEW_STATISTICS.checkForInput(MENU_MOUSE_POS):
                        pass
                    if NEWS.checkForInput(MENU_MOUSE_POS):
                        pass
                    if MY_PROFILE.checkForInput(MENU_MOUSE_POS):
                        pass
                    if PLAYER_PROFILE.checkForInput(MENU_MOUSE_POS):
                        pass
                    if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.options_window()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.set_player_offline()
                        self.vpn_client.set_vpn_state(False)
                        pygame.quit()
                        sys.exit()
                    if self._queue_status:
                        if CANCEL_QUEUE.checkForInput(MENU_MOUSE_POS):
                            get_time = False
                            self._queue_status = False
                            self._player_found = False
                            refresh_queue_window = True
                            is_playing = False
                            found_game = False  # TODO: remove this - ONLY FOR TESTING
                            pygame.mixer.Channel(0).set_volume(bg_sound_volume)
                            pygame.mixer.Channel(queue_channel).stop()
                        if ACCEPT_QUEUE is not None:
                            if ACCEPT_QUEUE.checkForInput(MENU_MOUSE_POS):
                                self._queue_status = False
                                self._player_found = False
                                self._game_accepted = True
                                found_game = False

            pygame.display.update()

    def queue_window(self):
        overlay_width, overlay_height = (
            self.config["screen_width"] // 3,
            self.config["screen_hight"] // 3,
        )
        self.QUEUE_BG = pygame.transform.scale(
            self.QUEUE_BG, (overlay_width, overlay_height)
        )
        overlay_surface = pygame.Surface((overlay_width, overlay_height))
        overlay_surface.fill((200, 200, 200))
        pygame.draw.rect(overlay_surface, (0, 0, 0), overlay_surface.get_rect(), 5)

        CANCEL_BUTTON = Button(
            image=self.CANCEL_BUTTON,
            image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
            pos=(overlay_width * 1.5, overlay_height * 1.8),
            text_input="Cancel",
            font=self.get_font(self.font_size[1]),
            base_color="#d7fcd4",
            hovering_color="White",
        )

        OPONNENT_TEXT = None
        OPONNENT_RECT = None
        HEADER_TEXT = None
        HEADER_RECT = None
        ACCEPT_BUTTON = None

        if self._player_found:
            HEADER_TEXT = self.get_font(self.font_size[0]).render(
                "GAME FOUND", True, "white"
            )
            HEADER_RECT = HEADER_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() / 2.4,
                )
            )

            OPONNENT_TEXT = self.get_font(self.font_size[0]).render(
                f"Opponent: Piotrek", True, "white"
            )
            if self.opponent_str != "":
                OPONNENT_TEXT = self.get_font(self.font_size[0]).render(
                    f"Opponent: {self.opponent_str}", True, "white"
                )
            OPONNENT_RECT = OPONNENT_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() / 2,
                )
            )
            ACCEPT_BUTTON = Button(
                image=self.ACCEPT_BUTTON,
                image_highlited=self.ACCEPT_BUTTON_HIGHLIGHTED,
                pos=(overlay_width * 1.3, overlay_height * 1.8),
                text_input="Accept",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            CANCEL_BUTTON = Button(
                image=self.CANCEL_BUTTON,
                image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
                pos=(overlay_width * 1.7, overlay_height * 1.8),
                text_input="Cancel",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )

        if self._game_accepted:
            game = AschanArena3_Game()
            game.run_processes()

        return (
            overlay_surface,
            CANCEL_BUTTON,
            ACCEPT_BUTTON,
            HEADER_TEXT,
            HEADER_RECT,
            OPONNENT_TEXT,
            OPONNENT_RECT,
        )

    def options_window(self):
        RESOLUTION_CHOICES = OptionBox(
            (self.SCREEN.get_width() / 6.5),
            (self.SCREEN.get_height() / 3.9),
            160,
            40,
            (150, 150, 150),
            (100, 200, 255),
            pygame.font.SysFont(None, 30),
            resolution_choices,
            resolution_choices.index(self.transformation_option),
        )

        while True:
            self.SCREEN.blit(self.BG, (0, 0))

            OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

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
                base_color="#d7fcd4",
                hovering_color="White",
            )
            self.SCREEN.blit(RESOLUTION_TEXT, RESOLUTION_RECT)

            for button in [BACK_BUTTON]:
                button.changeColor(OPTIONS_MOUSE_POS)
                button.update(self.SCREEN, OPTIONS_MOUSE_POS)

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    self.set_player_offline()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
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

    def set_player_offline(self):
        url = "http://4.231.97.96:8000/set_player_offline/"
        user_data = {"nickname": self.vpn_client.user_name}
        requests.post(url, json=user_data)

    def run_game(self):
        self.main_menu()
