import pygame
import os
import sys
import requests

from src.global_vars import fonts_sizes, bg_sound_volume
from src.lobby import H5_Lobby
from src.helpers import delete_objects
from src.vpn_handling import SoftEtherClient
from src.settings_reader import load_resolution_settings
from window_elements.text_input import TextInput
from window_elements.button import Button


class LoginWindow:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Heroes V of Might and Magic Ashan Arena 3 - Login")
        pygame.mixer.init()
        pygame.mixer.Channel(0).play(
            pygame.mixer.Sound(
                os.path.join(os.getcwd(), "resources/H5_login_menu_theme.mp3")
            ),
            -1,
            0,
        )
        pygame.mixer.Channel(0).set_volume(bg_sound_volume)

        self.transformation_option = "800x600"
        self.config = load_resolution_settings()
        self.font_size = fonts_sizes[self.transformation_option]

        self.SCREEN = pygame.display.set_mode((800, 600))
        self.BG = pygame.image.load(
            os.path.join(os.getcwd(), "resources/background/background.png")
        )
        self.BG = pygame.transform.scale(
            self.BG,
            (800, 600),
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

    def get_font(self, font_size: int = 75):
        return pygame.font.Font("resources/Quivira.otf", font_size)

    def login_window(self):
        self.BUTTON = pygame.transform.scale(
            self.BUTTON,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )
        self.BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.BUTTON_HIGHLIGHTED,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )

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
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 2.8),
                ),
                text_input="Login",
                font=self.get_font(font_size=30),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            LOGIN_BUTTON.changeColor(MENU_MOUSE_POS)
            LOGIN_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)

            REGISTER_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 4),
                ),
                text_input="Register",
                font=self.get_font(font_size=30),
                base_color="#d7fcd4",
                hovering_color="White",
            )

            REGISTER_BUTTON.changeColor(MENU_MOUSE_POS)
            REGISTER_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)

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
            REGISTER_ACCOUNT_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)

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
            BACK_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)

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
        # url = "http://4.231.97.96:8000/login/"
        # user_data = {
        #     "nickname": inputs[0].get_string(),
        #     "password": inputs[1].get_string(),
        # }
        # response = requests.post(url, json=user_data)

        # if response.status_code == 200:
        pygame.mixer.fadeout(5000)
        pygame.quit()
        self.vpn_client = SoftEtherClient("Kaczk0vsky")
        # self.vpn_client = SoftEtherClient(user_data["nickname"])
        self.vpn_client.set_vpn_state(state=True)
        lobby = H5_Lobby(self.vpn_client)
        lobby.run_game()

        # TODO: wrong password or login window
        return False

    def register_new_player(self, inputs: list):
        url = "http://4.231.97.96:8000/register/"
        client_private_key, client_public_key = SoftEtherClient.generate_keys()
        user_data = {
            "nickname": inputs[0].get_string(),
            "password": inputs[1].get_string(),
            "repeat_password": inputs[2].get_string(),
            "email": inputs[3].get_string(),
            "client_private_key": client_private_key,
            "client_public_key": client_public_key,
        }
        data = requests.get(url)
        response = requests.post(url, json=user_data)

        # TODO: add handling of different error codes
        if response.status_code == 200 and data.status_code == 200:
            data = data.json()
            SoftEtherClient.create_new_client(
                client=user_data["nickname"],
                server_public_key="pJD0nHGtw+EpgTMd4HZh4zHaBiWfXHzuEOLBcDM2ZyE=",
                client_private_key=user_data["client_private_key"],
                client_ip=data["last_available_ip"],
            )
            return True
        return False

    def run_game(self):
        self.login_window()
