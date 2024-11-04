import pygame
import os
import sys

from django.contrib.auth import authenticate

from src.global_vars import fonts_sizes
from src.lobby import H5_Lobby
from src.helpers import delete_objects
from window_elements.text_input import TextInput
from window_elements.button import Button


class LoginWindow:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Heroes V of Might and Magic Ashan Arena 3 - Login")
        pygame.mixer.init()
        self.mixer = pygame.mixer.music.load(
            os.path.join(os.getcwd(), "resources/H5_login_menu_theme.mp3")
        )
        self.mixer = pygame.mixer.music.play(-1, 0.0)
        self.mixer = pygame.mixer.music.set_volume(0.3)

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
        LOGIN_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            self.SCREEN.get_height() / 2.5,
            200,
            40,
            is_active=True,
        )
        PASSWORD_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1, self.SCREEN.get_height() / 2, 200, 40
        )
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
                    self.SCREEN.get_height() / 2.3,
                )
            )
            PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Password", True, "white"
            )
            PASSWORD_RECT = PASSWORD_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    self.SCREEN.get_height() / 1.9,
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
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 3.3),
                ),
                text_input="Login",
                font=self.get_font(font_size=30),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            LOGIN_BUTTON.changeColor(MENU_MOUSE_POS)
            LOGIN_BUTTON.update(self.SCREEN)

            REGISTER_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 10),
                ),
                text_input="Register",
                font=self.get_font(font_size=30),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            REGISTER_BUTTON.changeColor(MENU_MOUSE_POS)
            REGISTER_BUTTON.update(self.SCREEN)

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for input, is_hidden in zip(INPUT_BOXES, HIDE_INPUT):
                    input.event(event, is_hidden)
                    if input._enter_pressed == True and input.active:
                        self.login_player(INPUT_BOXES)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if LOGIN_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.login_player(INPUT_BOXES)
                    if REGISTER_BUTTON.checkForInput(MENU_MOUSE_POS):
                        delete_objects(INPUT_BOXES)
                        self.register_player()

            for input in INPUT_BOXES:
                input.update()
                input.draw(self.SCREEN)

            pygame.display.update()

    def register_player(self):
        NICKNAME_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            self.SCREEN.get_height() / 5.7,
            200,
            40,
            is_active=True,
            window_type="register",
        )
        PASSWORD_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            (self.SCREEN.get_height() / 5.7) + 50,
            200,
            40,
            window_type="register",
        )
        REPEAT_PASSWORD_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            (self.SCREEN.get_height() / 5.7) + 100,
            200,
            40,
            window_type="register",
        )
        EMAIL_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            (self.SCREEN.get_height() / 5.7) + 150,
            200,
            40,
            window_type="register",
        )
        INPUT_BOXES = [
            NICKNAME_INPUT,
            PASSWORD_INPUT,
            REPEAT_PASSWORD_INPUT,
            EMAIL_INPUT,
        ]
        HIDE_INPUT = [False, True, True, False]

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            NICKNAME_TEXT = self.get_font(self.font_size[0]).render(
                "Username", True, "white"
            )
            NICKNAME_RECT = NICKNAME_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    self.SCREEN.get_height() / 5,
                )
            )
            PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Password", True, "white"
            )
            PASSWORD_RECT = PASSWORD_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    (self.SCREEN.get_height() / 5) + 50,
                )
            )
            REPEAT_PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Repeat Password", True, "white"
            )
            REPEAT_PASSWORD_RECT = REPEAT_PASSWORD_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    (self.SCREEN.get_height() / 5) + 100,
                )
            )
            EMAIL_TEXT = self.get_font(self.font_size[0]).render("Email", True, "white")
            EMAIL_RECT = PASSWORD_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    (self.SCREEN.get_height() / 5) + 150,
                )
            )

            self.SCREEN.blit(NICKNAME_TEXT, NICKNAME_RECT)
            self.SCREEN.blit(PASSWORD_TEXT, PASSWORD_RECT)
            self.SCREEN.blit(REPEAT_PASSWORD_TEXT, REPEAT_PASSWORD_RECT)
            self.SCREEN.blit(EMAIL_TEXT, EMAIL_RECT)

            REGISTER_ACCOUNT_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 3.3),
                ),
                text_input="Register account",
                font=self.get_font(font_size=30),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            REGISTER_ACCOUNT_BUTTON.changeColor(MENU_MOUSE_POS)
            REGISTER_ACCOUNT_BUTTON.update(self.SCREEN)

            BACK_BUTTON = Button(
                image=pygame.image.load(
                    os.path.join(os.getcwd(), "resources/rectangle.png")
                ),
                pos=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 3.3) + 120,
                ),
                text_input="Back",
                font=self.get_font(font_size=30),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            BACK_BUTTON.changeColor(MENU_MOUSE_POS)
            BACK_BUTTON.update(self.SCREEN)

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for input, is_hidden in zip(INPUT_BOXES, HIDE_INPUT):
                    input.event(event, is_hidden)
                    if input._enter_pressed == True and input.active:
                        if_succesfull = self.register_new_player(INPUT_BOXES)
                        if if_succesfull:
                            delete_objects(INPUT_BOXES)
                            self.login_window()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if REGISTER_ACCOUNT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        if_succesfull = self.register_new_player(INPUT_BOXES)
                        if if_succesfull:
                            delete_objects(INPUT_BOXES)
                            self.login_window()
                    elif BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                        delete_objects(INPUT_BOXES)
                        self.login_window()

            for input in INPUT_BOXES:
                input.update()
                input.draw(self.SCREEN)

            pygame.display.update()

    def login_player(self, inputs: list):
        user_data = {
            "nickname": inputs[0].get_string(),
            "password": inputs[1].get_string(),
        }

        user = authenticate(
            username=user_data["nickname"], password=user_data["password"]
        )
        if user is not None:
            pygame.mixer.fadeout(5000)
            pygame.quit()
            lobby = H5_Lobby()
            lobby.run_game()

        # TODO: wrong password or login window

    def register_new_player(self, inputs: list):
        from django.contrib.auth.models import User

        user_data = {
            "nickname": inputs[0].get_string(),
            "password": inputs[1].get_string(),
            "repeat_password": inputs[2].get_string(),
            "email": inputs[3].get_string(),
        }
        if (
            user_data["password"] != user_data["repeat_password"]
            or "@" not in user_data["email"]
        ):
            # TODO: add the error msg window
            return False

        user = User.objects.create_user(
            username=user_data["nickname"],
            password=user_data["password"],
            email=user_data["email"],
        )
        if user is not None:
            return True
        return False

    def run_game(self):
        self.login_window()
