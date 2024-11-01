import pygame
import os
import sys

from django.contrib.auth import authenticate

from src.global_vars import fonts_sizes
from window_elements.text_input import TextInput
from window_elements.button import Button
from src.lobby import H5_Lobby


class LoginWindow:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Login menu")
        pygame.mixer.init()
        pygame.mixer.music.load(
            os.path.join(os.getcwd(), "resources/H5_login_menu_theme.mp3")
        )
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(0.3)

        self.transformation_option = "800x600"
        self.font_size = fonts_sizes[self.transformation_option]

        self.SCREEN = pygame.display.set_mode((800, 600))
        self.BG = pygame.image.load(os.path.join(os.getcwd(), "resources/h5_login.jpg"))
        self.BG = pygame.transform.scale(
            self.BG,
            (800, 600),
        )

    def get_font(self, font_size: int = 75):
        return pygame.font.Font("resources/ASansrounded.ttf", font_size)

    def login_window(self):
        LOGIN_INPUT = TextInput(380, 225, 200, 40, is_active=True)
        PASSWORD_INPUT = TextInput(380, 315, 200, 40)
        INPUT_BOXES = [LOGIN_INPUT, PASSWORD_INPUT]
        HIDE_INPUT = [False, True]

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            LOGIN_TEXT = self.get_font(self.font_size[0]).render(
                "Username", True, "white"
            )
            LOGIN_RECT = LOGIN_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    self.SCREEN.get_height() / 2.5,
                )
            )
            PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Password", True, "white"
            )
            PASSWORD_RECT = PASSWORD_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    self.SCREEN.get_height() / 1.8,
                )
            )

            self.SCREEN.blit(LOGIN_TEXT, LOGIN_RECT)
            self.SCREEN.blit(PASSWORD_TEXT, PASSWORD_RECT)

            LOGIN_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 4),
                ),
                text_input="Login",
                font=self.get_font(font_size=30),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            LOGIN_BUTTON.changeColor(MENU_MOUSE_POS)
            LOGIN_BUTTON.update(self.SCREEN)

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for input, is_hidden in zip(INPUT_BOXES, HIDE_INPUT):
                    input.event(event, is_hidden)
                    if input._enter_pressed == True and input.active:
                        self.login_player(LOGIN_INPUT, PASSWORD_INPUT)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if LOGIN_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.login_player(LOGIN_INPUT, PASSWORD_INPUT)

            for input in INPUT_BOXES:
                input.update()
                input.draw(self.SCREEN)

            pygame.display.update()

    def login_player(self, LOGIN_INPUT, PASSWORD_INPUT):
        nickname = LOGIN_INPUT.get_string()
        password = PASSWORD_INPUT.get_string()
        user = authenticate(username=nickname, password=password)
        if user is not None:
            pygame.mixer.fadeout(5000)
            pygame.quit()
            lobby = H5_Lobby()
            lobby.run_game()

    def run_game(self):
        self.login_window()
