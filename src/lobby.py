import pygame
import os
import toml
import time
import requests
import random
import ctypes
import webbrowser

from pygame.locals import *

from src.global_vars import (
    resolution_choices,
    points_choices,
    transformation_factors,
    fonts_sizes,
    env_dict,
    discord_invite,
)
from src.basic_window import GameWindowsBase
from src.run_ashan_arena import AschanArena3Game
from src.helpers import play_on_empty, calculate_time_passed, get_window, format_state, render_small_caps, check_server_connection
from src.custom_thread import CustomThread
from src.decorators import run_in_thread
from src.settings_writer import save_client_settings
from widgets.button import Button
from widgets.option_box import OptionBox
from widgets.progress_bar import ProgressBar
from widgets.users_list import UsersList
from widgets.check_box import CheckBox
from widgets.hover_box import HoverBox
from widgets.slider import Slider


class H5_Lobby(GameWindowsBase):
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

    __window_overlay = False
    __game_found_music = False
    __get_time = False
    __found_game = False
    __opponent_accepted = False
    __opponent_declined = False
    __player_accepted = False
    __queue_status = False
    __update_queue_status = False
    __update_game_data = False
    __profile_status = False
    __update_profile_status = False
    __options_status = False
    __update_options_status = False
    __queue_canceled = False
    __reconnect_back_to_game = False
    __is_connected = True
    __has_disconnected = False
    __elapsed_time = None
    __queue_channel = None
    __error_msg = None
    __connection_timer = None
    __game_data = None

    def __init__(
        self,
        vpn_client: object,
        user: dict,
        crsf_token: str,
        session: requests.Session,
    ):
        GameWindowsBase.__init__(self)

        self.vpn_client = vpn_client
        self.user = user
        self.crsf_token = crsf_token
        self.session = session
        self.transformation_option = self.config["resolution"]
        self.font_size = fonts_sizes[self.transformation_option]

        self.set_window_caption(title="Menu")
        self.play_background_music(music_path="resources/H5_main_theme.mp3")
        self.create_lobby_elements()

        self.resolution = (int(self.config["resolution"].split("x")[0]), int(self.config["resolution"].split("x")[1]))
        self.SCREEN = pygame.display.set_mode(self.resolution)

    def __set_queue_variables(self, state: bool = False) -> None:
        self.__game_found_music = state
        self.__get_time = state
        self.__found_game = state
        self.__opponent_accepted = state
        self.__player_accepted = state
        self.__queue_status = state
        self.__elapsed_time = None
        self.__queue_channel = None
        self.__connection_timer = None

    def main_menu(self):
        self.rescale_lobby_elements()

        FIND_GAME_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(
                830 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            text_input="Find Game",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        RANKING = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(
                1060 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            text_input="Ranking",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        NEWS = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(
                1290 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            text_input="News",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        MY_PROFILE = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(
                1520 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            text_input="My Profile",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        DISCORD = Button(
            image=self.DISCORD_LOGO,
            image_highlited=self.DISCORD_LOGO_HIGHLIGHTED,
            position=(
                1660 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        PLAYER_PROFILE = Button(
            image=self.ICON_SQUARE,
            image_highlited=self.ICON_SQUARE_HIGHLIGHTED,
            image_inactive=self.ICON_SQUARE,
            position=(
                1730 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )
        OPTIONS_BUTTON = Button(
            image=self.OPTIONS,
            image_highlited=self.OPTIONS_HIGHLIGHTED,
            image_inactive=self.OPTIONS,
            position=(
                1800 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )
        QUIT_BUTTON = Button(
            image=self.QUIT_LOBBY,
            image_highlited=self.QUIT_LOBBY_HIGHLIGHTED,
            position=(
                1870 * (transformation_factors[self.transformation_option][0]),
                50 * (transformation_factors[self.transformation_option][1]),
            ),
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        USERS_LIST = UsersList(
            position=(
                1710 * (transformation_factors[self.transformation_option][0]),
                590 * (transformation_factors[self.transformation_option][1]),
            ),
            color=self.text_color,
            font_size=self.font_size[0],
            title="Players Online",
            image=self.PLAYER_LIST,
            image_bg=self.PLAYER_LIST_BG,
            image_box=self.PLAYER_LIST_FRAME,
            scroll=self.SCROLL,
            scroll_bar=self.SCROLL_BAR,
            line=self.LINE,
            box=self.CHECKBOX,
        )
        self.refresh_friends_list(USERS_LIST)
        self.get_user_profile()

        buttons = [FIND_GAME_BUTTON, RANKING, NEWS, MY_PROFILE, DISCORD, PLAYER_PROFILE, OPTIONS_BUTTON, QUIT_BUTTON]
        widgets = buttons + [USERS_LIST]

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

            for button in buttons:
                button.handle_button(self.SCREEN, MENU_MOUSE_POS)

            try:
                USERS_LIST.update(self.SCREEN)
            except pygame.error:
                continue

            if self.__queue_status:
                if self.__update_queue_status:
                    (
                        CANCEL_QUEUE,
                        ACCEPT_QUEUE,
                        OPONNENT_TEXT,
                        OPONNENT_RECT,
                        PROGRESS_BAR,
                    ) = self.queue_window()
                    ACCEPT_QUEUE.set_active(False) if self.__player_accepted else None
                    self.__update_queue_status = False

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
                if not self.__found_game:
                    minutes, seconds = calculate_time_passed(self.start_time)
                    HEADER_TEXT = render_small_caps(f"Waiting for opponent: {minutes}:{seconds:02d}", self.font_size[0], self.text_color)
                    HEADER_RECT = HEADER_TEXT.get_rect(
                        center=(
                            self.SCREEN.get_width() / 2,
                            self.SCREEN.get_height() / 2.4,
                        )
                    )
                else:
                    HEADER_TEXT = render_small_caps("Game Found", int(self.font_size[0] * 2), self.hovering_color)
                    HEADER_RECT = HEADER_TEXT.get_rect(
                        center=(
                            self.SCREEN.get_width() / 2,
                            self.SCREEN.get_height() / 2.4,
                        )
                    )
                self.SCREEN.blit(HEADER_TEXT, HEADER_RECT)
                if OPONNENT_TEXT is not None and OPONNENT_RECT is not None:
                    self.SCREEN.blit(OPONNENT_TEXT, OPONNENT_RECT)
                if PROGRESS_BAR is not None and not self.__player_accepted:
                    cancel_bar = PROGRESS_BAR.draw(self.SCREEN, self.__elapsed_time)
                    if cancel_bar:
                        self.__window_overlay = True
                        self.__queue_canceled = True
                        self.__error_msg = "Queue has been declined"
                        pygame.mixer.Channel(0).set_volume(self.config["volume"])
                        pygame.mixer.Channel(self.__queue_channel).stop()
                        FIND_GAME_BUTTON.set_active(is_active=True)
                        self.__set_queue_variables(state=False)
                        self.remove_from_queue(is_accepted=False)
                        continue

            if self.__game_data:
                if self.__update_game_data:
                    FIND_GAME_BUTTON.set_active(is_active=False)
                    (
                        RESULT_TEXT,
                        RESULT_RECT,
                        MYSELF_TEXT,
                        MYSELF_RECT,
                        MYSELF_POINTS,
                        MYSELF_POINTS_RECT,
                        OPPONENT_TEXT,
                        OPPONENT_RECT,
                        OPPONENT_POINTS,
                        OPPONENT_POINTS_RECT,
                        SUBMIT_REPORT,
                    ) = self.report_window()
                    SUBMIT_REPORT.set_active(True)
                    self.__update_game_data = False

                self.SCREEN.blit(
                    self.SMALLER_WINDOWS_BG,
                    (
                        640 * transformation_factors[self.transformation_option][0],
                        360 * transformation_factors[self.transformation_option][1],
                    ),
                )
                self.SCREEN.blit(RESULT_TEXT, RESULT_RECT)
                self.SCREEN.blit(MYSELF_TEXT, MYSELF_RECT)
                self.SCREEN.blit(MYSELF_POINTS, MYSELF_POINTS_RECT)
                self.SCREEN.blit(OPPONENT_TEXT, OPPONENT_RECT)
                self.SCREEN.blit(OPPONENT_POINTS, OPPONENT_POINTS_RECT)
                SUBMIT_REPORT.handle_button(self.SCREEN, MENU_MOUSE_POS)

            if self.__profile_status or self.__options_status:
                self.SCREEN.blit(
                    self.LEFT_FRAME,
                    (self.frame_position[0], self.frame_position[1]),
                )

            if self.__profile_status:
                if self.__update_profile_status:
                    (
                        NICKNAME_TEXT,
                        NICKNAME_RECT,
                        NICKNAME_LINE,
                        POINTS_TEXT,
                        POINTS_RECT,
                        POINTS_LINE,
                        RANKING_POSITION_TEXT,
                        RANKING_POSITION_RECT,
                        RANKING_POSITION_LINE,
                        RANKED_STATICTICS_TEXT,
                        RANKED_STATISTICS_RECT,
                        RANKED_GAMES_PLAYED_TEXT,
                        RANKED_GAMES_PLAYED_RECT,
                        RANKED_WINS_LOSES_TEXT,
                        RANKED_WINS_LOSES_RECT,
                        RANKED_WINARTIO_TEXT,
                        RANKED_WINRATIO_RECT,
                        RANKED_POSITION_LINE,
                        UNRANKED_STATICTICS_TEXT,
                        UNRANKED_STATISTICS_RECT,
                        UNRANKED_GAMES_PLAYED_TEXT,
                        UNRANKED_GAMES_PLAYED_RECT,
                        UNRANKED_WINS_LOSES_TEXT,
                        UNRANKED_WINS_LOSES_RECT,
                        UNRANKED_WINARTIO_TEXT,
                        UNRANKED_WINRATIO_RECT,
                        UNRANKED_POSITION_LINE,
                        TOTAL_STATICTICS_TEXT,
                        TOTAL_STATISTICS_RECT,
                        TOTAL_GAMES_PLAYED_TEXT,
                        TOTAL_GAMES_PLAYED_RECT,
                        TOTAL_WINS_LOSES_TEXT,
                        TOTAL_WINS_LOSES_RECT,
                        TOTAL_WINARTIO_TEXT,
                        TOTAL_WINRATIO_RECT,
                        CLOSE_BUTTON,
                    ) = self.profile_window()
                    self.__update_profile_status = False

                self.SCREEN.blit(
                    self.LEFT_FRAME,
                    (self.frame_position[0], self.frame_position[1]),
                )
                self.SCREEN.blit(NICKNAME_TEXT, NICKNAME_RECT)
                self.SCREEN.blit(self.WIDE_LINE, NICKNAME_LINE)
                self.SCREEN.blit(POINTS_TEXT, POINTS_RECT)
                self.SCREEN.blit(self.NARROW_LINE, POINTS_LINE)
                self.SCREEN.blit(RANKING_POSITION_TEXT, RANKING_POSITION_RECT)
                self.SCREEN.blit(self.NARROW_LINE, RANKING_POSITION_LINE)
                self.SCREEN.blit(RANKED_STATICTICS_TEXT, RANKED_STATISTICS_RECT)
                self.SCREEN.blit(RANKED_GAMES_PLAYED_TEXT, RANKED_GAMES_PLAYED_RECT)
                self.SCREEN.blit(RANKED_WINS_LOSES_TEXT, RANKED_WINS_LOSES_RECT)
                self.SCREEN.blit(RANKED_WINARTIO_TEXT, RANKED_WINRATIO_RECT)
                self.SCREEN.blit(self.NARROW_LINE, RANKED_POSITION_LINE)
                self.SCREEN.blit(UNRANKED_STATICTICS_TEXT, UNRANKED_STATISTICS_RECT)
                self.SCREEN.blit(UNRANKED_GAMES_PLAYED_TEXT, UNRANKED_GAMES_PLAYED_RECT)
                self.SCREEN.blit(UNRANKED_WINS_LOSES_TEXT, UNRANKED_WINS_LOSES_RECT)
                self.SCREEN.blit(UNRANKED_WINARTIO_TEXT, UNRANKED_WINRATIO_RECT)
                self.SCREEN.blit(self.NARROW_LINE, UNRANKED_POSITION_LINE)
                self.SCREEN.blit(TOTAL_STATICTICS_TEXT, TOTAL_STATISTICS_RECT)
                self.SCREEN.blit(TOTAL_GAMES_PLAYED_TEXT, TOTAL_GAMES_PLAYED_RECT)
                self.SCREEN.blit(TOTAL_WINS_LOSES_TEXT, TOTAL_WINS_LOSES_RECT)
                self.SCREEN.blit(TOTAL_WINARTIO_TEXT, TOTAL_WINRATIO_RECT)
                CLOSE_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)

            if self.__options_status:
                if self.__update_options_status:
                    (
                        SETTINGS_TEXT,
                        SETTINGS_RECT,
                        SETTINGS_LINE,
                        RESOLUTION_TEXT,
                        RESOLUTION_RECT,
                        RESOLUTION_CHOICES,
                        RESOLUTION_LINE,
                        VOLUME_TEXT,
                        VOLUME_RECT,
                        VOLUME_SLIDER,
                        VOLUME_LINE,
                        POINTS_TRESHOLD_TEXT,
                        POINTS_TRESHOLD_RECT,
                        POINTS_CHOICES,
                        POINTS_HOVER_BOX,
                        POINTS_TRESHOLD_LINE,
                        RANKED_TEXT,
                        RANKED_RECT,
                        RANKED_LINE,
                        CHECKBOX_RANKED,
                        CLOSE_BUTTON,
                    ) = self.options_window()
                    self.__update_options_status = False

                self.SCREEN.blit(SETTINGS_TEXT, SETTINGS_RECT)
                self.SCREEN.blit(self.WIDE_LINE, SETTINGS_LINE)
                self.SCREEN.blit(RESOLUTION_TEXT, RESOLUTION_RECT)
                self.SCREEN.blit(self.NARROW_LINE, RESOLUTION_LINE)
                self.SCREEN.blit(VOLUME_TEXT, VOLUME_RECT)
                self.SCREEN.blit(self.NARROW_LINE, VOLUME_LINE)
                self.SCREEN.blit(POINTS_TRESHOLD_TEXT, POINTS_TRESHOLD_RECT)
                POINTS_HOVER_BOX.update(self.SCREEN, MENU_MOUSE_POS)
                self.SCREEN.blit(self.NARROW_LINE, POINTS_TRESHOLD_LINE)
                self.SCREEN.blit(RANKED_TEXT, RANKED_RECT)
                self.SCREEN.blit(self.NARROW_LINE, RANKED_LINE)
                CHECKBOX_RANKED.update(self.SCREEN)
                CLOSE_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)
                RESOLUTION_CHOICES.update(self.SCREEN, MENU_MOUSE_POS)
                POINTS_CHOICES.update(self.SCREEN, MENU_MOUSE_POS)
                VOLUME_SLIDER.draw(self.SCREEN)
                VOLUME_SLIDER.update_slider(MENU_MOUSE_POS)

            if self.__error_msg:
                (WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT, RETURN_BUTTON) = self.error_window(
                    text=self.__error_msg,
                    dimensions=(
                        640 * transformation_factors[self.transformation_option][0],
                        360 * transformation_factors[self.transformation_option][1],
                    ),
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
                if not self.__connection_timer:
                    RETURN_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)

            for event in pygame.event.get():
                USERS_LIST.event(event)
                if event.type == pygame.QUIT:
                    if self.__queue_status:
                        self.remove_from_queue(is_accepted=False)
                    self.quit_game_handling(self.crsf_token, self.session)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if FIND_GAME_BUTTON.check_for_input(MENU_MOUSE_POS):
                        self.__update_queue_status = True
                        self.__queue_status = True
                        FIND_GAME_BUTTON.set_active(is_active=False)
                        self.add_to_queue()
                        continue
                    if RANKING.check_for_input(MENU_MOUSE_POS):
                        pass
                    if NEWS.check_for_input(MENU_MOUSE_POS):
                        pass
                    if MY_PROFILE.check_for_input(MENU_MOUSE_POS):
                        self.__update_profile_status = True
                        self.__profile_status = True
                        if self.__options_status:
                            save_client_settings(self.config)
                            self.__options_status = False
                        continue
                    if DISCORD.check_for_input(MENU_MOUSE_POS):
                        webbrowser.open(discord_invite)
                    if PLAYER_PROFILE.check_for_input(MENU_MOUSE_POS):
                        pass
                    if OPTIONS_BUTTON.check_for_input(MENU_MOUSE_POS):
                        self.__update_options_status = True
                        self.__options_status = True
                        if self.__profile_status:
                            self.__profile_status = False
                        continue
                    if QUIT_BUTTON.check_for_input(MENU_MOUSE_POS):
                        if self.__queue_status:
                            self.remove_from_queue(is_accepted=False)
                        self.quit_game_handling(self.crsf_token, self.session)
                    if self.__queue_status:
                        if CANCEL_QUEUE.check_for_input(MENU_MOUSE_POS):
                            pygame.mixer.Channel(0).set_volume(self.config["volume"])
                            if self.__queue_channel:
                                pygame.mixer.Channel(self.__queue_channel).stop()
                            FIND_GAME_BUTTON.set_active(is_active=True)
                            self.__set_queue_variables(state=False)
                            self.remove_from_queue(is_accepted=False)
                            continue
                        if ACCEPT_QUEUE is not None:
                            if ACCEPT_QUEUE.check_for_input(MENU_MOUSE_POS):
                                self.__update_queue_status = True
                                self.__player_accepted = True
                                FIND_GAME_BUTTON.set_active(is_active=False)
                                self.remove_from_queue(is_accepted=True)
                                self.check_if_oponnent_accepted()

                    if self.__game_data:
                        if SUBMIT_REPORT.check_for_input(MENU_MOUSE_POS):
                            FIND_GAME_BUTTON.set_active(is_active=True)
                            self.__update_game_data = False
                            self.__game_data = None

                    if self.__profile_status:
                        if CLOSE_BUTTON.check_for_input(MENU_MOUSE_POS):
                            self.__update_profile_status = False
                            self.__profile_status = False

                    if self.__window_overlay:
                        if self.__error_msg:
                            if RETURN_BUTTON.check_for_input(MENU_MOUSE_POS):
                                if self.__queue_canceled:
                                    self.__queue_canceled = False
                                self.__window_overlay = False
                                self.__error_msg = None

                    if self.__options_status:
                        if self.__profile_status:
                            self.__profile_status = False
                        if RESOLUTION_CHOICES.check_for_input(MENU_MOUSE_POS):
                            self.config["resolution"] = str(RESOLUTION_CHOICES.get_selected_option())
                            self.transformation_option = self.config["resolution"]
                            self.resolution = (int(self.config["resolution"].split("x")[0]), int(self.config["resolution"].split("x")[1]))
                            self.SCREEN = pygame.display.set_mode(self.resolution)
                            self.BG = pygame.transform.scale(
                                self.BG,
                                self.resolution,
                            )
                            self.rescale_lobby_elements(reload=True)
                            for button in buttons:
                                button.rescale(fonts_sizes[self.config["resolution"]][0], transformation_factors[self.config["resolution"]])
                        if POINTS_CHOICES.check_for_input(MENU_MOUSE_POS):
                            self.config["points_treshold"] = str(POINTS_CHOICES.get_selected_option())
                        if POINTS_HOVER_BOX.check_for_input(MENU_MOUSE_POS):
                            pass
                        if CHECKBOX_RANKED.check_for_input(MENU_MOUSE_POS):
                            self.config["is_ranked"] = not self.config["is_ranked"]
                        if CLOSE_BUTTON.check_for_input(MENU_MOUSE_POS):
                            save_client_settings(self.config)
                            self.__options_status = False

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.__options_status:
                        self.config["volume"] = VOLUME_SLIDER.get_slider_value() / 100
                        if self.__found_game:
                            pygame.mixer.Channel(self.__queue_channel).set_volume(self.config["volume"])
                        else:
                            pygame.mixer.Channel(0).set_volume(self.config["volume"])

            if (self.__opponent_accepted and self.__player_accepted) or (self.__reconnect_back_to_game and self.__is_connected):
                if self.__queue_channel:
                    pygame.mixer.Channel(self.__queue_channel).stop()
                pygame.mixer.Channel(0).set_volume(0.0)
                self.__set_queue_variables(state=False)
                self.run_arena()
                continue

            if self.__opponent_declined:
                self.__update_queue_status = True
                self.__opponent_declined = False
                self.__found_game = False
                self.__player_accepted = False
                self.__game_found_music = False
                self.__elapsed_time = None
                pygame.mixer.Channel(0).set_volume(self.config["volume"])
                if self.__queue_channel:
                    pygame.mixer.Channel(self.__queue_channel).stop()
                self.add_to_queue()

            if self.__connection_timer:
                time_passed = calculate_time_passed(start_time=self.__connection_timer)
                if time_passed[0] >= 1:
                    self.__window_overlay = True
                    self.__error_msg = f"Connecting for {time_passed[0]}:{time_passed[1]} minutes..."
                elif time_passed[1] >= 3:
                    self.__window_overlay = True
                    self.__error_msg = f"Connecting for {time_passed[1]} seconds..."

                if self.__is_connected and not self.__queue_canceled:
                    self.__connection_timer = None
                    self.__error_msg = None
                    FIND_GAME_BUTTON.set_active(True)
                    RANKING.set_active(True)
                    NEWS.set_active(True)

            if self.__has_disconnected:
                # TODO: add something that disables the buttons to not let the player click to much
                FIND_GAME_BUTTON.set_active(False)
                RANKING.set_active(False)
                NEWS.set_active(False)
                self.check_connection_state()
                self.__has_disconnected = False

            pygame.display.update()

    def queue_window(self):
        dims = (
            640 * transformation_factors[self.transformation_option][0],
            360 * transformation_factors[self.transformation_option][1],
        )
        self.SMALLER_WINDOWS_BG = pygame.transform.scale(self.SMALLER_WINDOWS_BG, dims)

        if not self.__get_time:
            self.start_time = time.time()
            self.__get_time = True

        CANCEL_BUTTON = Button(
            image=self.CANCEL_BUTTON,
            image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
            position=(dims[0] * 1.5, dims[1] * 1.8),
            text_input="Cancel",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )

        ACCEPT_BUTTON = None
        OPONNENT_TEXT = None
        OPONNENT_RECT = None
        PROGRESS_BAR = None

        if self.__found_game:
            if not self.__elapsed_time:
                self.__elapsed_time = time.time()
            if not self.__game_found_music:
                self.__queue_channel = play_on_empty("resources/match_found.wav", volume=self.config["volume"])
                pygame.mixer.Channel(0).set_volume(0.0)
                self.__game_found_music = True

            if self.__player_accepted:
                information_str = f"Waiting for {self.__opponent_nickname} to accept..."
            else:
                information_str = f"{self.__opponent_nickname} - {self.__oponnent_ranking_points} PKT"
            OPONNENT_TEXT = render_small_caps(information_str, self.font_size[0], self.text_color)
            OPONNENT_RECT = OPONNENT_TEXT.get_rect(center=(self.SCREEN.get_width() / 2, self.SCREEN.get_height() / 2.12))
            ACCEPT_BUTTON = Button(
                image=self.ACCEPT_BUTTON,
                image_highlited=self.ACCEPT_BUTTON_HIGHLIGHTED,
                image_inactive=self.ACCEPT_BUTTON_INACTIVE,
                position=(dims[0] * 1.3, dims[1] * 1.8),
                text_input="Accept",
                font_size=self.font_size[1],
                base_color=self.text_color,
                hovering_color=self.hovering_color,
                inactive_color=self.inactive_color,
            )
            CANCEL_BUTTON = Button(
                image=self.CANCEL_BUTTON,
                image_highlited=self.CANCEL_BUTTON_HIGHLIGHTED,
                image_inactive=self.CANCEL_BUTTON_INACTIVE,
                position=(dims[0] * 1.7, dims[1] * 1.8),
                text_input="Cancel",
                font_size=self.font_size[1],
                base_color=self.text_color,
                hovering_color=self.hovering_color,
                inactive_color=self.inactive_color,
            )
            if not self.__player_accepted:
                PROGRESS_BAR = ProgressBar(
                    position=(dims[0] * 1.5, dims[1] * 1.6),
                    dimensions=(dims[0] * 0.9, dims[1] * 0.175),
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

    def profile_window(self):
        NICKNAME_TEXT = render_small_caps(self.user["nickname"], int(self.font_size[0] * 1.75), self.hovering_color)
        NICKNAME_RECT = NICKNAME_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.15)
        )
        NICKNAME_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.1875)

        POINTS_TEXT = render_small_caps(f"{self.__profile_data['ranking_points']} PKT", int(self.font_size[0]), self.text_color)
        POINTS_RECT = POINTS_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.225)
        )
        POINTS_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.2625)

        RANKING_POSITION_TEXT = render_small_caps(
            f"Ranking position: {self.__profile_data['ranking_position']}", int(self.font_size[0]), self.text_color
        )
        RANKING_POSITION_RECT = RANKING_POSITION_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.305)
        )
        RANKING_POSITION_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.3425)

        RANKED_STATICTICS_TEXT = render_small_caps("Ranked Statistics", int(self.font_size[0]), self.text_color)
        RANKED_STATISTICS_RECT = RANKED_STATICTICS_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.375)
        )

        RANKED_GAMES_PLAYED_TEXT = render_small_caps(
            f"Games played: {self.__profile_data['ranked_games'][0] + self.__profile_data['ranked_games'][1]}",
            int(self.font_size[1]),
            self.text_color,
        )
        RANKED_GAMES_PLAYED_RECT = RANKED_GAMES_PLAYED_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.41)
        )

        RANKED_WINS_LOSES_TEXT = render_small_caps(
            f"Wins/Loses: {self.__profile_data['ranked_games'][0]}/{self.__profile_data['ranked_games'][1]}",
            int(self.font_size[1]),
            self.text_color,
        )
        RANKED_WINS_LOSES_RECT = RANKED_WINS_LOSES_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.44)
        )

        try:
            winrate = (
                self.__profile_data["ranked_games"][0] / (self.__profile_data["ranked_games"][0] + self.__profile_data["ranked_games"][1])
            ) * 100
        except ZeroDivisionError:
            winrate = 0

        RANKED_WINARTIO_TEXT = render_small_caps(f"Win rate: {round(winrate, 2)} %", int(self.font_size[1]), self.text_color)
        RANKED_WINRATIO_RECT = RANKED_WINARTIO_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.47)
        )
        RANKED_POSITION_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.5)

        UNRANKED_STATICTICS_TEXT = render_small_caps("Unranked Statistics", int(self.font_size[0]), self.text_color)
        UNRANKED_STATISTICS_RECT = UNRANKED_STATICTICS_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.5375)
        )

        UNRANKED_GAMES_PLAYED_TEXT = render_small_caps(
            f"Games played: {self.__profile_data['unranked_games'][0] + self.__profile_data['unranked_games'][1]}",
            int(self.font_size[1]),
            self.text_color,
        )
        UNRANKED_GAMES_PLAYED_RECT = UNRANKED_GAMES_PLAYED_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.5725)
        )

        UNRANKED_WINS_LOSES_TEXT = render_small_caps(
            f"Wins/Loses: {self.__profile_data['unranked_games'][0]}/{self.__profile_data['unranked_games'][1]}",
            int(self.font_size[1]),
            self.text_color,
        )
        UNRANKED_WINS_LOSES_RECT = UNRANKED_WINS_LOSES_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.6075)
        )

        try:
            winrate = (
                self.__profile_data["unranked_games"][0] / (self.__profile_data["unranked_games"][0] + self.__profile_data["unranked_games"][1])
            ) * 100
        except ZeroDivisionError:
            winrate = 0
        UNRANKED_WINARTIO_TEXT = render_small_caps(f"Win rate: {round(winrate, 2)} %", int(self.font_size[1]), self.text_color)
        UNRANKED_WINRATIO_RECT = UNRANKED_WINARTIO_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.6425)
        )
        UNRANKED_POSITION_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.6725)

        TOTAL_STATICTICS_TEXT = render_small_caps("Total Statistics", int(self.font_size[0]), self.text_color)
        TOTAL_STATISTICS_RECT = TOTAL_STATICTICS_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.71)
        )

        TOTAL_GAMES_PLAYED_TEXT = render_small_caps(f"Games played: {self.__profile_data['total_games']}", int(self.font_size[1]), self.text_color)
        TOTAL_GAMES_PLAYED_RECT = TOTAL_GAMES_PLAYED_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.745)
        )

        total_wins = self.__profile_data["ranked_games"][0] + self.__profile_data["unranked_games"][0]
        total_loses = self.__profile_data["ranked_games"][1] + self.__profile_data["unranked_games"][1]
        TOTAL_WINS_LOSES_TEXT = render_small_caps(f"Wins/Loses: {total_wins}/{total_loses}", int(self.font_size[1]), self.text_color)
        TOTAL_WINS_LOSES_RECT = TOTAL_WINS_LOSES_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.78)
        )

        try:
            winrate = (total_wins / (total_wins + total_loses)) * 100
        except ZeroDivisionError:
            winrate = 0
        TOTAL_WINARTIO_TEXT = render_small_caps(f"Win rate: {round(winrate, 2)} %", int(self.font_size[1]), self.text_color)
        TOTAL_WINRATIO_RECT = TOTAL_WINARTIO_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.815)
        )

        CLOSE_BUTTON = Button(
            image=self.QUIT_FRAME,
            image_highlited=self.QUIT_FRAME_HIGHLIGHTED,
            position=(self.frame_position[0] + self.frame_dims[0] * 0.875, self.frame_position[1] + self.frame_dims[1] * 0.0875),
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )

        return (
            NICKNAME_TEXT,
            NICKNAME_RECT,
            NICKNAME_LINE,
            POINTS_TEXT,
            POINTS_RECT,
            POINTS_LINE,
            RANKING_POSITION_TEXT,
            RANKING_POSITION_RECT,
            RANKING_POSITION_LINE,
            RANKED_STATICTICS_TEXT,
            RANKED_STATISTICS_RECT,
            RANKED_GAMES_PLAYED_TEXT,
            RANKED_GAMES_PLAYED_RECT,
            RANKED_WINS_LOSES_TEXT,
            RANKED_WINS_LOSES_RECT,
            RANKED_WINARTIO_TEXT,
            RANKED_WINRATIO_RECT,
            RANKED_POSITION_LINE,
            UNRANKED_STATICTICS_TEXT,
            UNRANKED_STATISTICS_RECT,
            UNRANKED_GAMES_PLAYED_TEXT,
            UNRANKED_GAMES_PLAYED_RECT,
            UNRANKED_WINS_LOSES_TEXT,
            UNRANKED_WINS_LOSES_RECT,
            UNRANKED_WINARTIO_TEXT,
            UNRANKED_WINRATIO_RECT,
            UNRANKED_POSITION_LINE,
            TOTAL_STATICTICS_TEXT,
            TOTAL_STATISTICS_RECT,
            TOTAL_GAMES_PLAYED_TEXT,
            TOTAL_GAMES_PLAYED_RECT,
            TOTAL_WINS_LOSES_TEXT,
            TOTAL_WINS_LOSES_RECT,
            TOTAL_WINARTIO_TEXT,
            TOTAL_WINRATIO_RECT,
            CLOSE_BUTTON,
        )

    def report_window(self):
        dims = (
            640 * transformation_factors[self.transformation_option][0],
            360 * transformation_factors[self.transformation_option][1],
        )
        overlay_dims = (
            510 * transformation_factors[self.transformation_option][0],
            390 * transformation_factors[self.transformation_option][1],
        )
        self.SMALLER_WINDOWS_BG = pygame.transform.scale(self.SMALLER_WINDOWS_BG, (overlay_dims[0], overlay_dims[1]))

        if self.__game_data["is_won"]:
            result_text = "VICTORY"
            result_color = "#02ba09"
            player_points = self.__game_data["winner"][1]
            player_points_change = f"(+{self.__game_data['winner'][2]})"
            opponent_nickname = self.__game_data["loser"][0]
            opponent_points = self.__game_data["loser"][1]
            opponent_points_change = f"(-{self.__game_data['loser'][2]})"
        else:
            result_text = "DEFEAT"
            result_color = "#db1102"
            player_points_change = f"(-{self.__game_data['loser'][2]})"
            player_points = self.__game_data["loser"][1]
            opponent_nickname = self.__game_data["winner"][0]
            opponent_points = self.__game_data["winner"][1]
            opponent_points_change = f"(+{self.__game_data['winner'][2]})"

        opponent_color = "#02ba09" if result_color == "#db1102" else "#db1102"

        RESULT_TEXT = render_small_caps(result_text, int(self.font_size[0] * 1.5), result_color)
        RESULT_RECT = RESULT_TEXT.get_rect(center=(dims[0] + overlay_dims[0] * 0.5, dims[1] + overlay_dims[1] * 0.2))

        MYSELF_TEXT = render_small_caps(f"{self.user["nickname"]}: ", self.font_size[0], self.text_color)
        MYSELF_POINTS = render_small_caps(f"{player_points} {player_points_change}", self.font_size[0], result_color)
        total_width = MYSELF_TEXT.get_width() + MYSELF_POINTS.get_width()
        start_x = (dims[0] + overlay_dims[0] * 0.5) - (total_width / 2)
        start_y = dims[1] + overlay_dims[1] * 0.375
        MYSELF_RECT = MYSELF_TEXT.get_rect(topleft=(start_x, start_y))
        MYSELF_POINTS_RECT = MYSELF_POINTS.get_rect(topleft=(MYSELF_RECT.right, start_y))

        OPPONENT_TEXT = render_small_caps(f"{opponent_nickname}: ", self.font_size[0], self.text_color)
        OPPONENT_POINTS = render_small_caps(f"{opponent_points} {opponent_points_change}", self.font_size[0], opponent_color)
        total_width = OPPONENT_TEXT.get_width() + OPPONENT_POINTS.get_width()
        start_x = (dims[0] + overlay_dims[0] * 0.5) - (total_width / 2)
        start_y = dims[1] + overlay_dims[1] * 0.5
        OPPONENT_RECT = OPPONENT_TEXT.get_rect(topleft=(start_x, start_y))
        OPPONENT_POINTS_RECT = OPPONENT_POINTS.get_rect(topleft=(OPPONENT_RECT.right, start_y))

        SUBMIT_REPORT = Button(
            image=self.ACCEPT_BUTTON,
            image_highlited=self.ACCEPT_BUTTON_HIGHLIGHTED,
            image_inactive=self.ACCEPT_BUTTON_INACTIVE,
            position=(dims[0] + overlay_dims[0] * 0.5, dims[1] + overlay_dims[1] * 0.8),
            text_input="Confirm",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )

        return (
            RESULT_TEXT,
            RESULT_RECT,
            MYSELF_TEXT,
            MYSELF_RECT,
            MYSELF_POINTS,
            MYSELF_POINTS_RECT,
            OPPONENT_TEXT,
            OPPONENT_RECT,
            OPPONENT_POINTS,
            OPPONENT_POINTS_RECT,
            SUBMIT_REPORT,
        )

    def options_window(self):
        SETTINGS_TEXT = render_small_caps("Settings", int(self.font_size[0] * 1.5), self.text_color)
        SETTINGS_RECT = SETTINGS_TEXT.get_rect(
            center=(self.frame_position[0] + self.frame_dims[0] * 0.5, self.frame_position[1] + self.frame_dims[1] * 0.15)
        )
        SETTINGS_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.1875)

        RESOLUTION_TEXT = render_small_caps("Resolution:", self.font_size[0], self.text_color)
        RESOLUTION_RECT = RESOLUTION_TEXT.get_rect(
            topleft=(self.frame_position[0] + self.frame_dims[0] * 0.125, self.frame_position[1] + self.frame_dims[1] * 0.21)
        )
        RESOLUTION_CHOICES = OptionBox(
            position=(self.frame_position[0] + self.frame_dims[0] * 0.675, self.frame_position[1] + self.frame_dims[1] * 0.235),
            dimensions=self.option_box_dims,
            arrow_left=self.ARROW_LEFT,
            arrow_left_highlighted=self.ARROW_LEFT_HIGHLIGHTED,
            arrow_right=self.ARROW_RIGHT,
            arrow_right_highlighted=self.ARROW_RIGHT_HIGHLIGHTED,
            color=self.text_color,
            highlight_color=self.hovering_color,
            font_size=self.font_size[1],
            option_list=resolution_choices,
            selected=self.config["resolution"],
        )
        RESOLUTION_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.28)

        VOLUME_TEXT = render_small_caps("Volume:", self.font_size[0], self.text_color)
        VOLUME_RECT = VOLUME_TEXT.get_rect(
            topleft=(self.frame_position[0] + self.frame_dims[0] * 0.125, self.frame_position[1] + self.frame_dims[1] * 0.3025)
        )
        VOLUME_SLIDER = Slider(
            position=(self.frame_position[0] + self.frame_dims[0] * 0.35, self.frame_position[1] + self.frame_dims[1] * 0.31),
            scroll=self.SETTINGS_SCROLL_BAR,
            scroll_marker=self.SETTINGS_SCROLL_MARKER,
            color=self.text_color,
            font_size=self.font_size[1],
            selected_value=self.config["volume"] * 100,
        )
        VOLUME_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.3725)

        POINTS_TRESHOLD_TEXT = render_small_caps("Rating Floor:", self.font_size[0], self.text_color)
        POINTS_TRESHOLD_RECT = POINTS_TRESHOLD_TEXT.get_rect(
            topleft=(self.frame_position[0] + self.frame_dims[0] * 0.125, self.frame_position[1] + self.frame_dims[1] * 0.395)
        )
        POINTS_CHOICES = OptionBox(
            position=(self.frame_position[0] + self.frame_dims[0] * 0.675, self.frame_position[1] + self.frame_dims[1] * 0.42),
            dimensions=self.option_box_dims,
            arrow_left=self.ARROW_LEFT,
            arrow_left_highlighted=self.ARROW_LEFT_HIGHLIGHTED,
            arrow_right=self.ARROW_RIGHT,
            arrow_right_highlighted=self.ARROW_RIGHT_HIGHLIGHTED,
            color=self.text_color,
            highlight_color=self.hovering_color,
            font_size=self.font_size[1],
            option_list=points_choices,
            selected=self.config["points_treshold"],
        )
        POINTS_HOVER_BOX = HoverBox(
            image=self.QUESTION_MARK,
            image_highlited=self.QUESTION_MARK_HIGHLIGHTED,
            position=(self.frame_position[0] + self.frame_dims[0] * 0.85, self.frame_position[1] + self.frame_dims[1] * 0.42),
        )
        POINTS_TRESHOLD_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.465)

        RANKED_TEXT = render_small_caps("Ranked games:", self.font_size[0], self.text_color)
        RANKED_RECT = RANKED_TEXT.get_rect(
            topleft=(self.frame_position[0] + self.frame_dims[0] * 0.125, self.frame_position[1] + self.frame_dims[1] * 0.4875)
        )
        CHECKBOX_RANKED = CheckBox(
            position=(self.frame_position[0] + self.frame_dims[0] * 0.7, self.frame_position[1] + self.frame_dims[1] * 0.515),
            image=self.CHECKBOX_SETTINGS,
            image_checked=self.CHECKBOX_SETTINGS_CHECKED,
            checked=self.config["is_ranked"],
        )
        RANKED_LINE = (self.frame_position[0] + self.frame_dims[0] * 0.1, self.frame_position[1] + self.frame_dims[1] * 0.5575)

        CLOSE_BUTTON = Button(
            image=self.QUIT_FRAME,
            image_highlited=self.QUIT_FRAME_HIGHLIGHTED,
            position=(self.frame_position[0] + self.frame_dims[0] * 0.875, self.frame_position[1] + self.frame_dims[1] * 0.0875),
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )

        return (
            SETTINGS_TEXT,
            SETTINGS_RECT,
            SETTINGS_LINE,
            RESOLUTION_TEXT,
            RESOLUTION_RECT,
            RESOLUTION_CHOICES,
            RESOLUTION_LINE,
            VOLUME_TEXT,
            VOLUME_RECT,
            VOLUME_SLIDER,
            VOLUME_LINE,
            POINTS_TRESHOLD_TEXT,
            POINTS_TRESHOLD_RECT,
            POINTS_CHOICES,
            POINTS_HOVER_BOX,
            POINTS_TRESHOLD_LINE,
            RANKED_TEXT,
            RANKED_RECT,
            RANKED_LINE,
            CHECKBOX_RANKED,
            CLOSE_BUTTON,
        )

    @run_in_thread
    def add_to_queue(self):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict["PATH_ADD"]}/"
        if not self.crsf_token:
            self.__window_overlay = True
            self.__error_msg = "Please login again."
            return

        user_data = {
            "nickname": self.user["nickname"],
            "is_searching_ranked": self.config["is_ranked"],
            "min_opponent_points": self.config["points_treshold"],
        }
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }
        self.__connection_timer = time.time()
        try:
            response = self.session.post(url, json=user_data, headers=headers)
            if response.status_code == 200:
                self.__connection_timer = None
                self.scan_for_players()

            else:
                self.__window_overlay = True
                self.__connection_timer = None
                self.__error_msg = response.json().get("error", "Unknown error occurred")

        except requests.exceptions.ConnectTimeout:
            self.__has_disconnected = True
            self.__window_overlay = True
            self.__error_msg = "Error while trying to connect to server!"

        except requests.exceptions.ConnectionError:
            self.__has_disconnected = True
            self.__window_overlay = True
            self.__error_msg = "Error! Check your internet connection..."

        except:
            self.__has_disconnected = True
            self.__window_overlay = True
            self.__error_msg = "Error! Server/Player offline, check discord..."

    @run_in_thread
    def remove_from_queue(self, is_accepted: bool):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict["PATH_REMOVE"]}/"
        if not self.crsf_token:
            self.__window_overlay = True
            self.__error_msg = "Please login again."
            return

        user_data = {
            "nickname": self.user["nickname"],
            "is_accepted": is_accepted,
        }
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }
        self.__connection_timer = time.time()
        try:
            response = self.session.post(url, json=user_data, headers=headers)
            if response.status_code == 200:
                self.__connection_timer = None

            else:
                self.__window_overlay = True
                self.__connection_timer = None
                self.__error_msg = response.json().get("error", "Unknown error occurred")

        except requests.exceptions.ConnectTimeout:
            self.__has_disconnected = True
            self.__window_overlay = True
            self.__error_msg = "Error while trying to connect to server!"

        except requests.exceptions.ConnectionError:
            self.__has_disconnected = True
            self.__window_overlay = True
            self.__error_msg = "Error! Check your internet connection..."

        except:
            self.__has_disconnected = True
            self.__window_overlay = True
            self.__error_msg = "Error! Server/Player offline, check discord..."

    @run_in_thread
    def scan_for_players(self):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict["PATH_GET_PLAYERS"]}/"
        if not self.crsf_token:
            self.__window_overlay = True
            self.__error_msg = "Please login again."
            return

        user_data = {"nickname": self.user["nickname"]}
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }

        while True:
            try:
                if not self.__queue_status:
                    break
                self.__connection_timer = time.time()
                response = self.session.post(url, json=user_data, headers=headers)
                if response.status_code == 200:
                    self.__connection_timer = None
                    json_response = response.json()
                    if json_response.get("game_found"):
                        self.__update_queue_status = True
                        self.__found_game = True
                        self.__opponent_nickname = json_response.get("opponent")[0]
                        self.__oponnent_ranking_points = json_response.get("opponent")[1]
                        break

            except requests.exceptions.ConnectTimeout:
                self.__has_disconnected = True
                self.__error_msg = "Error while trying to connect to server!"
                return

            except requests.exceptions.ConnectionError:
                self.__has_disconnected = True
                self.__error_msg = "Error! Check your internet connection..."
                return

            except:
                self.__has_disconnected = True
                self.__error_msg = "Error! Server/Player offline, check discord..."
                return

            time.sleep(random.randint(1, 5))

    @run_in_thread
    def check_if_oponnent_accepted(self):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict['PATH_CHECK_OPONNENT']}/"
        if not self.crsf_token:
            self.__window_overlay = True
            self.__error_msg = "Please login again."
            return

        user_data = {"nickname": self.user["nickname"]}
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }

        while True:
            self.__connection_timer = time.time()
            try:
                response = self.session.post(url, json=user_data, headers=headers)
                if response.status_code == 200:
                    self.__connection_timer = None
                    json_response = response.json()
                    if json_response.get("opponent_accepted"):
                        self.__opponent_accepted = True
                        break
                    elif json_response.get("opponent_declined"):
                        self.__opponent_declined = True
                        break

            except requests.exceptions.ConnectTimeout:
                self.__has_disconnected = True
                self.__error_msg = "Error while trying to connect to server!"
                return

            except requests.exceptions.ConnectionError:
                self.__has_disconnected = True
                self.__error_msg = "Error! Check your internet connection..."
                return

            except:
                self.__has_disconnected = True
                self.__error_msg = "Error! Server/Player offline, check discord..."
                return

            time.sleep(1)

    @run_in_thread
    def refresh_friends_list(self, users_list: UsersList):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict['PATH_TO_USERS_LIST']}/"
        if not self.crsf_token:
            self.__window_overlay = True
            self.__error_msg = "Please login again."
            return

        user_data = {"nickname": self.user["nickname"]}
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
                    players_data = json_response.get("players_data")
                    sorted_players = {
                        player: (score, format_state(state))
                        for player, (score, state) in sorted(
                            players_data.items(),
                            key=lambda item: item[1][0],
                            reverse=True,
                        )
                    }
                    users_list.get_players_list(sorted_players)

            except Exception as e:
                pass

            time.sleep(15)

    @run_in_thread
    def handle_match_report(self, is_won: bool, castle: str):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict['PATH_TO_REPORT']}/"
        if not self.crsf_token:
            self.__window_overlay = True
            self.__error_msg = "Please login again."
            return

        user_data = {
            "nickname": self.user["nickname"],
            "is_won": is_won,
            "castle": castle,
        }
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }

        self.__connection_timer = time.time()
        try:
            response = self.session.post(url, json=user_data, headers=headers)
            if response.status_code == 200:
                self.__game_data = response.json().get("game_data")
                self.__game_data["is_won"] = is_won
                self.__update_game_data = True
                self.__connection_timer = None
                # Reload profile information
                self.get_user_profile()
                return True

            elif response.status_code == 400:
                self.__window_overlay = True
                self.__connection_timer = None
                return response.json().get("error", "Unknown error occurred")

        except requests.exceptions.ConnectTimeout:
            self.__has_disconnected = True
            self.__window_overlay = True
            return "Error while trying to connect to server!"

        except requests.exceptions.ConnectionError:
            self.__has_disconnected = True
            self.__window_overlay = True
            return "Error while trying to connect to server!"

        except:
            self.__has_disconnected = True
            self.__window_overlay = True
            return "Error! Server/Player offline, check discord..."

    @run_in_thread
    def get_user_profile(self):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict['PATH_TO_PROFILE']}/"
        if not self.crsf_token:
            self.__window_overlay = True
            self.__error_msg = "Please login again."
            return

        user_data = {"nickname": self.user["nickname"]}
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }

        try:
            response = self.session.get(url, params=user_data, headers=headers)
            if response.status_code == 200:
                self.__profile_data = response.json().get("player_information")
                return True

            elif response.status_code == 400:
                self.__window_overlay = True
                return response.json().get("error", "Unknown error occurred")

        except requests.exceptions.ConnectTimeout:
            self.__window_overlay = True
            return "Error while trying to connect to server!"

        except requests.exceptions.ConnectionError:
            self.__window_overlay = True
            return "Error while trying to connect to server!"

        except:
            self.__window_overlay = True
            return "Error! Server/Player offline, check discord..."

    @run_in_thread
    def set_player_online(self):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict["PATH_PLAYER_ONLINE"]}/"
        if not self.crsf_token:
            self.__window_overlay = True
            self.__error_msg = "Please login again."
            return

        user_data = {"nickname": self.vpn_client.user_name}
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.crsf_token,
            "Content-Type": "application/json",
        }
        self.__connection_timer = time.time()
        try:
            response = self.session.post(url, json=user_data, headers=headers)
            if response.status_code == 200:
                self.__connection_timer = None
                return

            elif response.status_code == 400:
                self.__window_overlay = True
                self.__connection_timer = None

        except requests.exceptions.ConnectTimeout:
            self.__has_disconnected = True
            self.__window_overlay = True
            return "Error while trying to connect to server!"

        except requests.exceptions.ConnectionError:
            self.__has_disconnected = True
            self.__window_overlay = True
            return "Error while trying to connect to server!"

        except:
            self.__has_disconnected = True
            self.__window_overlay = True
            return "Error! Server/Player offline, check discord..."

    @run_in_thread
    def check_connection_state(self):
        self.__connection_timer = time.time()
        self.__window_overlay = True
        self.__queue_status = False
        self.__is_connected = False
        self.__elapsed_time = None

        while not self.__is_connected:
            if check_server_connection():
                self.__is_connected = True
                return
            else:
                pass
            time.sleep(5)

    def minimize_to_tray(self):
        time.sleep(0.1)
        self.window = get_window()
        self.window.minimize()
        self.window.hide()
        pygame.display.iconify()

    def maximize_from_tray(self):
        self.window.restore()
        hwnd = self.window._hWnd
        ctypes.windll.user32.ShowWindow(hwnd, 9)
        foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
        current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        foreground_thread_id = ctypes.windll.user32.GetWindowThreadProcessId(foreground_hwnd, 0)
        if foreground_thread_id != current_thread_id:
            ctypes.windll.user32.AttachThreadInput(current_thread_id, foreground_thread_id, True)
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.BringWindowToTop(hwnd)
        if foreground_thread_id != current_thread_id:
            ctypes.windll.user32.AttachThreadInput(current_thread_id, foreground_thread_id, False)
        self.play_background_music(music_path="resources/H5_main_theme.mp3")

    def run_game(self):
        self.main_menu()

    def run_arena(self):
        game = AschanArena3Game(self)
        time.sleep(2)
        game.run_processes()

        self.__reconnect_back_to_game = game._reconnect_back_to_game
        self.__has_disconnected = game._has_disconnected
        if self.__has_disconnected:
            self.__connection_timer = time.time()
            self.__is_connected = False
