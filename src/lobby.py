from src.global_vars import load_initial_window_setting
from window_elements.button import Button
from window_elements.option_box import OptionBox

from pygame.locals import *

import pygame
import sys
import os


class H5_Lobby:
    def __init__(self):
        pygame.init()
        self.config = load_initial_window_setting()

        self.SCREEN = pygame.display.set_mode(
            (self.config["screen_width"], self.config["screen_hight"]), pygame.RESIZABLE
        )
        self.BG = pygame.image.load(
            os.path.join(os.getcwd(), "resources/h5_background.jpg")
        )
        pygame.display.set_caption("Menu")

    def get_font(self, font_size: int = 75):
        return pygame.font.Font("resources/ASansrounded.ttf", font_size)

    def main_menu(self):
        while True:
            self.SCREEN.blit(self.BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = self.get_font(50).render("H5 Lobby Launcher", True, "#b68f40")
            MENU_RECT = MENU_TEXT.get_rect(center=(290, 220))

            font_size = 50
            FIND_GAME_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(290, 350),
                text_input="Find Game",
                font=self.get_font(font_size),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            VIEW_STATISTICS = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(290, 500),
                text_input="View Statistics",
                font=self.get_font(font_size),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            OPTIONS_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(290, 650),
                text_input="Options",
                font=self.get_font(font_size),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            QUIT_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(290, 800),
                text_input="Quit Game",
                font=self.get_font(font_size),
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

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if FIND_GAME_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pass
                    if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.options_window()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

    def options_window(self):
        choices = [
            "640x480",
            "800x600",
            "1280x720",
            "1600x1200",
            "1920x1080",
            "1920x1440",
            "2560x1440",
            "Fullscreen",
        ]
        RESOLUTION_CHOICES = OptionBox(
            40,
            40,
            160,
            40,
            (150, 150, 150),
            (100, 200, 255),
            pygame.font.SysFont(None, 30),
            choices,
        )

        while True:
            self.SCREEN.blit(self.BG, (0, 0))

            OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = self.get_font(50).render("H5 Lobby Launcher", True, "#b68f40")
            MENU_RECT = MENU_TEXT.get_rect(center=(290, 220))

            font_size = 50
            BACK_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(290, 800),
                text_input="Quit Game",
                font=self.get_font(font_size),
                base_color="#d7fcd4",
                hovering_color="White",
            )
            self.SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [BACK_BUTTON]:
                button.changeColor(OPTIONS_MOUSE_POS)
                button.update(self.SCREEN)

            event_list = pygame.event.get()
            # print(event_list) if len(event_list) > 0 else None
            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                        self.main_menu()

            selected_option = RESOLUTION_CHOICES.update(event_list)
            if selected_option != -1:
                resolution = choices[selected_option]
                if "fullscreen" in resolution.lower():
                    monitor_resolution = pygame.display.Info()
                    self.SCREEN = pygame.display.set_mode(
                        (monitor_resolution.current_w, monitor_resolution.current_h),
                        pygame.FULLSCREEN,
                    )
                else:
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

            RESOLUTION_CHOICES.draw(self.SCREEN)
            pygame.display.update()

    def run_game(self):
        self.main_menu()
