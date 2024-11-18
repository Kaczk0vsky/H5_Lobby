from src.settings_reader import load_resolution_settings
from src.global_vars import resolution_choices, transformation_factors, fonts_sizes
from src.run_ashan_arena import AschanArena3_Game
from window_elements.button import Button
from window_elements.option_box import OptionBox

from pygame.locals import *

import pygame
import sys
import os
import toml
import requests


class H5_Lobby:
    _queue_status = False

    def __init__(self, vpn_client):
        pygame.init()
        pygame.display.set_caption("Heroes V of Might and Magic Ashan Arena 3 - Menu")
        pygame.mixer.init()
        pygame.mixer.music.load(
            os.path.join(os.getcwd(), "resources/H5_main_theme.mp3")
        )
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(0.3)
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
            os.path.join(os.getcwd(), "resources/h5_background.jpg")
        )
        self.QUEUE_BG = pygame.image.load(
            os.path.join(os.getcwd(), "resources/queue.jpg")
        )

    def get_font(self, font_size: int = 75):
        return pygame.font.Font("resources/ASansrounded.ttf", font_size)

    def main_menu(self):
        self.BG = pygame.transform.scale(
            self.BG,
            (self.config["screen_width"], self.config["screen_hight"]),
        )
        queue_window, CANCEL_QUEUE, ACCEPT_QUEUE = self.queue_window()
        queue_window_x = (self.config["screen_width"] - queue_window.get_width()) // 2
        queue_window_y = (self.config["screen_hight"] - queue_window.get_height()) // 2

        while True:
            self.SCREEN.blit(self.BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = self.get_font(self.font_size[0]).render(
                "H5 Lobby Launcher", True, "#b68f40"
            )
            MENU_RECT = MENU_TEXT.get_rect(
                center=(
                    290 * (transformation_factors[self.transformation_option][0]),
                    220 * (transformation_factors[self.transformation_option][1]),
                )
            )

            FIND_GAME_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(
                    290 * (transformation_factors[self.transformation_option][0]),
                    350 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="Find Game",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            VIEW_STATISTICS = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(
                    290 * (transformation_factors[self.transformation_option][0]),
                    500 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="View Statistics",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            OPTIONS_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(
                    290 * (transformation_factors[self.transformation_option][0]),
                    650 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="Options",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            QUIT_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(
                    290 * (transformation_factors[self.transformation_option][0]),
                    800 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="Quit",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            self.SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [
                FIND_GAME_BUTTON,
                VIEW_STATISTICS,
                OPTIONS_BUTTON,
                QUIT_BUTTON,
            ]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.SCREEN)

            if self._queue_status:
                self.SCREEN.blit(self.QUEUE_BG, (queue_window_x, queue_window_y))
                CANCEL_QUEUE.changeColor(MENU_MOUSE_POS)
                CANCEL_QUEUE.update(self.SCREEN)
                ACCEPT_QUEUE.changeColor(MENU_MOUSE_POS)
                ACCEPT_QUEUE.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if FIND_GAME_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self._queue_status = True
                    if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.options_window()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.set_player_offline()
                        self.vpn_client.set_vpn_state(False)
                        pygame.quit()
                        sys.exit()
                    if self._queue_status:
                        if CANCEL_QUEUE.checkForInput(MENU_MOUSE_POS):
                            self._queue_status = False
                        if ACCEPT_QUEUE.checkForInput(MENU_MOUSE_POS):
                            self._queue_status = False

            pygame.display.update()

    def queue_window(self):
        player_found = False
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
            image=pygame.image.load(
                os.path.join(os.getcwd(), "resources/rectangle.png")
            ),
            pos=(overlay_width * 1.8, overlay_height * 1.8),
            text_input="Cancel",
            font=self.get_font(self.font_size[1]),
            base_color="#d7fcd4",
            hovering_color="White",
        )

        ACCEPT_BUTTON = Button(
            image=pygame.image.load(
                os.path.join(os.getcwd(), "resources/rectangle.png")
            ),
            pos=(overlay_width * 1.2, overlay_height * 1.8),
            text_input="Accept",
            font=self.get_font(self.font_size[1]),
            base_color="#d7fcd4",
            hovering_color="White",
        )

        if player_found:
            game = AschanArena3_Game()
            game.run_processes()

        return overlay_surface, CANCEL_BUTTON, ACCEPT_BUTTON

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

            MENU_TEXT = self.get_font(self.font_size[0]).render(
                "H5 Lobby Launcher", True, "#FFFFFF"
            )
            MENU_RECT = MENU_TEXT.get_rect(
                center=(
                    290 * (transformation_factors[self.transformation_option][0]),
                    220 * (transformation_factors[self.transformation_option][1]),
                )
            )

            RESOLUTION_TEXT = self.get_font(self.font_size[1]).render(
                "Select resolution", True, "#FFFFFF"
            )
            RESOLUTION_RECT = RESOLUTION_TEXT.get_rect(
                center=(
                    130 * (transformation_factors[self.transformation_option][0]),
                    300 * transformation_factors[self.transformation_option][1],
                ),
            )

            BACK_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(
                    290 * (transformation_factors[self.transformation_option][0]),
                    800 * (transformation_factors[self.transformation_option][1]),
                ),
                text_input="Back",
                font=self.get_font(self.font_size[1]),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            self.SCREEN.blit(MENU_TEXT, MENU_RECT)
            self.SCREEN.blit(RESOLUTION_TEXT, RESOLUTION_RECT)

            for button in [BACK_BUTTON]:
                button.changeColor(OPTIONS_MOUSE_POS)
                button.update(self.SCREEN)

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
                with open(os.path.join(os.getcwd(), "settings.toml"), "w") as f:
                    toml.dump({"resolution": self.config}, f)

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
