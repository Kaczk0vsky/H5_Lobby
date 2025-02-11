import pygame
import os
import sys
import requests

from src.global_vars import fonts_sizes, bg_sound_volume
from src.lobby import H5_Lobby
from src.helpers import delete_objects
from src.vpn_handling import SoftEtherClient
from src.settings_reader import load_resolution_settings, load_client_settings
from src.settings_writer import save_login_information
from window_elements.text_input import TextInput
from window_elements.button import Button
from window_elements.check_box import CheckBox


class LoginWindow:
    _window_overlay = False
    _wrong_password_status = False
    _forgot_password_status = False

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
        self.text_color = "#d7fcd4"
        self.hovering_color = "White"
        self.config = load_resolution_settings()
        self.client_config = load_client_settings()
        self.font_size = fonts_sizes[self.transformation_option]

        self.SCREEN = pygame.display.set_mode((800, 600))
        self.BG = pygame.image.load(
            os.path.join(os.getcwd(), "resources/background/background.png")
        )
        self.BG = pygame.transform.scale(
            self.BG,
            (800, 600),
        )
        self.WRONG_PASSWORD_BG = pygame.image.load(
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

    def get_font(self, font_size: int = 75):
        return pygame.font.Font("resources/Quivira.otf", font_size)

    def login_window(self):
        def fix_main_window():
            self._forgot_password_status = False
            self._window_overlay = False
            LOGIN_INPUT.set_active(self.SCREEN)

        self.BUTTON = pygame.transform.scale(
            self.BUTTON,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )
        self.BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.BUTTON_HIGHLIGHTED,
            (self.config["screen_width"] / 9, self.config["screen_hight"] / 17),
        )
        self.LONG_BUTTON = pygame.transform.scale(
            self.BUTTON,
            (self.config["screen_width"] / 6, self.config["screen_hight"] / 17),
        )
        self.LONG_BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.BUTTON_HIGHLIGHTED,
            (self.config["screen_width"] / 6, self.config["screen_hight"] / 17),
        )
        CHECK_BOX_PASSWORD = CheckBox(
            self.SCREEN,
            self.SCREEN.get_width() / 1.7,
            self.SCREEN.get_height() / 1.675,
            20,
            20,
            self.client_config["remember_password"],
        )

        LOGIN_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            self.SCREEN.get_height() / 2.5,
            200,
            40,
            (
                self.client_config["nickname"]
                if self.client_config["remember_password"]
                else ""
            ),
            is_active=True,
        )
        PASSWORD_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            self.SCREEN.get_height() / 2,
            200,
            40,
            (
                self.client_config["password"]
                if self.client_config["remember_password"]
                else ""
            ),
        )
        INPUT_BOXES = [LOGIN_INPUT, PASSWORD_INPUT]
        HIDE_INPUT = [False, True]

        overlay_surface_x = 100
        overlay_surface_y = 100

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            LOGIN_TEXT = self.get_font(self.font_size[0]).render(
                "Username:", True, self.text_color
            )
            LOGIN_RECT = LOGIN_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    self.SCREEN.get_height() / 2.3,
                )
            )
            PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Password:", True, self.text_color
            )
            PASSWORD_RECT = PASSWORD_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    self.SCREEN.get_height() / 1.9,
                )
            )
            REMEMBER_LOGIN_TEXT = self.get_font(self.font_size[0]).render(
                "Remeber me:", True, self.text_color
            )
            REMEMBER_LOGIN_RECT = REMEMBER_LOGIN_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 2.1,
                    self.SCREEN.get_height() / 1.65,
                )
            )

            self.SCREEN.blit(LOGIN_TEXT, LOGIN_RECT)
            self.SCREEN.blit(PASSWORD_TEXT, PASSWORD_RECT)
            self.SCREEN.blit(REMEMBER_LOGIN_TEXT, REMEMBER_LOGIN_RECT)

            LOGIN_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 3.3),
                ),
                text_input="Login",
                font=self.get_font(font_size=30),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
            )

            REGISTER_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    self.SCREEN.get_width() / 2,
                    (self.SCREEN.get_height() - (self.SCREEN.get_height() / 3.3) + 65),
                ),
                text_input="Register",
                font=self.get_font(font_size=30),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
            )

            FORGOT_PASSWORD_BUTTON = Button(
                image=self.LONG_BUTTON,
                image_highlited=self.LONG_BUTTON_HIGHLIGHTED,
                pos=(
                    self.SCREEN.get_width() / 2,
                    (self.SCREEN.get_height() - (self.SCREEN.get_height() / 3.3) + 130),
                ),
                text_input="Forgot Password",
                font=self.get_font(font_size=30),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
            )

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
                    if not self._window_overlay:
                        if LOGIN_BUTTON.checkForInput(MENU_MOUSE_POS):
                            self.login_player(INPUT_BOXES)
                        if REGISTER_BUTTON.checkForInput(MENU_MOUSE_POS):
                            delete_objects(INPUT_BOXES)
                            self.register_player()
                        if FORGOT_PASSWORD_BUTTON.checkForInput(MENU_MOUSE_POS):
                            self._window_overlay = True
                            self._forgot_password_status = True
                        if CHECK_BOX_PASSWORD.checkForInput(MENU_MOUSE_POS):
                            self.client_config["remember_password"] = (
                                not self.client_config["remember_password"]
                            )
                    else:
                        if self._forgot_password_status:
                            if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                                fix_main_window()
                            if SUBMIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                                # TODO: send an email if the data is correct
                                fix_main_window()
                        elif self._wrong_password_status:
                            if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                                fix_main_window()

            if not self._window_overlay:
                buttons = [LOGIN_BUTTON, REGISTER_BUTTON, FORGOT_PASSWORD_BUTTON]

                CHECK_BOX_PASSWORD.update()
                for button in buttons:
                    button.changeColor(MENU_MOUSE_POS)
                    button.update(self.SCREEN, MENU_MOUSE_POS)
                for input in INPUT_BOXES:
                    input.update()
                    input.draw(self.SCREEN)

            if self._wrong_password_status:
                (WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT, BACK_BUTTON) = (
                    self.wrong_password_window()
                )

                self.SCREEN.blit(
                    self.WRONG_PASSWORD_BG, (overlay_surface_x, overlay_surface_y)
                )
                self.SCREEN.blit(WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT)
                BACK_BUTTON.changeColor(MENU_MOUSE_POS)
                BACK_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)

            if self._forgot_password_status:
                (
                    BACK_BUTTON,
                    SUBMIT_BUTTON,
                    NICKNAME_INPUT,
                    NICKNAME_TEXT,
                    NICKNAME_RECT,
                    EMAIL_INPUT,
                    EMAIL_TEXT,
                    EMAIL_RECT,
                ) = self.forgot_password_window()

                self.SCREEN.blit(
                    self.FORGOT_PASSWORD_BG, (overlay_surface_x, overlay_surface_y)
                )
                BACK_BUTTON.changeColor(MENU_MOUSE_POS)
                BACK_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)
                SUBMIT_BUTTON.changeColor(MENU_MOUSE_POS)
                SUBMIT_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)
                NICKNAME_INPUT.update()
                NICKNAME_INPUT.draw(self.SCREEN)
                EMAIL_INPUT.update()
                EMAIL_INPUT.draw(self.SCREEN)
                self.SCREEN.blit(NICKNAME_TEXT, NICKNAME_RECT)
                self.SCREEN.blit(EMAIL_TEXT, EMAIL_RECT)

            pygame.display.update()

    def register_player(self):
        NICKNAME_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            self.SCREEN.get_height() / 4.6,
            200,
            40,
            is_active=True,
        )
        PASSWORD_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            (self.SCREEN.get_height() / 4.6) + 50,
            200,
            40,
        )
        REPEAT_PASSWORD_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            (self.SCREEN.get_height() / 4.6) + 100,
            200,
            40,
        )
        EMAIL_INPUT = TextInput(
            self.SCREEN.get_width() / 2.1,
            (self.SCREEN.get_height() / 4.6) + 150,
            200,
            40,
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
                "Username", True, self.text_color
            )
            NICKNAME_RECT = NICKNAME_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    self.SCREEN.get_height() / 4,
                )
            )
            PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Password", True, self.text_color
            )
            PASSWORD_RECT = PASSWORD_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    (self.SCREEN.get_height() / 4) + 50,
                )
            )
            REPEAT_PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Repeat Password", True, self.text_color
            )
            REPEAT_PASSWORD_RECT = REPEAT_PASSWORD_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    (self.SCREEN.get_height() / 4) + 100,
                )
            )
            EMAIL_TEXT = self.get_font(self.font_size[0]).render(
                "Email", True, self.text_color
            )
            EMAIL_RECT = PASSWORD_TEXT.get_rect(
                center=(
                    self.SCREEN.get_width() / 3,
                    (self.SCREEN.get_height() / 4) + 150,
                )
            )

            self.SCREEN.blit(NICKNAME_TEXT, NICKNAME_RECT)
            self.SCREEN.blit(PASSWORD_TEXT, PASSWORD_RECT)
            self.SCREEN.blit(REPEAT_PASSWORD_TEXT, REPEAT_PASSWORD_RECT)
            self.SCREEN.blit(EMAIL_TEXT, EMAIL_RECT)

            REGISTER_ACCOUNT_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 2.6),
                ),
                text_input="Submit",
                font=self.get_font(font_size=30),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
            )

            REGISTER_ACCOUNT_BUTTON.changeColor(MENU_MOUSE_POS)
            REGISTER_ACCOUNT_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)

            BACK_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(
                    self.SCREEN.get_width() / 2,
                    self.SCREEN.get_height() - (self.SCREEN.get_height() / 2.6) + 120,
                ),
                text_input="Back",
                font=self.get_font(font_size=30),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
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

    def wrong_password_window(self):
        overlay_width, overlay_height = (
            600,
            400,
        )
        self.WRONG_PASSWORD_BG = pygame.transform.scale(
            self.WRONG_PASSWORD_BG, (overlay_width, overlay_height)
        )
        overlay_surface = pygame.Surface((overlay_width, overlay_height))
        overlay_surface.fill((200, 200, 200))
        pygame.draw.rect(overlay_surface, (0, 0, 0), overlay_surface.get_rect(), 5)

        WRONG_PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
            "Given password is not correct!", True, self.text_color
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

    def forgot_password_window(self):
        overlay_width, overlay_height = (
            600,
            400,
        )
        self.FORGOT_PASSWORD_BG = pygame.transform.scale(
            self.WRONG_PASSWORD_BG, (overlay_width, overlay_height)
        )
        overlay_surface = pygame.Surface((overlay_width, overlay_height))
        overlay_surface.fill((200, 200, 200))
        pygame.draw.rect(overlay_surface, (0, 0, 0), overlay_surface.get_rect(), 5)

        BACK_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            pos=(self.SCREEN.get_width() / 2, self.SCREEN.get_height() / 1.35),
            text_input="Back",
            font=self.get_font(self.font_size[0]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        SUBMIT_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            pos=(self.SCREEN.get_width() / 2, (self.SCREEN.get_height() / 1.35) - 60),
            text_input="Submit",
            font=self.get_font(self.font_size[0]),
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        NICKNAME_INPUT = TextInput(
            self.SCREEN.get_width() / 2,
            self.SCREEN.get_height() / 1.35 - 220,
            200,
            40,
            is_active=True,
        )
        EMAIL_INPUT = TextInput(
            self.SCREEN.get_width() / 2,
            self.SCREEN.get_height() / 1.35 - 160,
            200,
            40,
            is_active=False,
        )
        NICKNAME_TEXT = self.get_font(self.font_size[0]).render(
            "Username:", True, self.text_color
        )
        NICKNAME_RECT = NICKNAME_TEXT.get_rect(
            center=(
                (self.SCREEN.get_width() / 2) - 100,
                self.SCREEN.get_height() / 1.35 - 200,
            )
        )
        EMAIL_TEXT = self.get_font(self.font_size[0]).render(
            "Email:", True, self.text_color
        )
        EMAIL_RECT = EMAIL_TEXT.get_rect(
            center=(
                (self.SCREEN.get_width() / 2) - 100,
                self.SCREEN.get_height() / 1.35 - 140,
            )
        )

        return (
            BACK_BUTTON,
            SUBMIT_BUTTON,
            NICKNAME_INPUT,
            NICKNAME_TEXT,
            NICKNAME_RECT,
            EMAIL_INPUT,
            EMAIL_TEXT,
            EMAIL_RECT,
        )

    def login_player(self, inputs: list):
        # url = "http://4.231.97.96:8000/login/"
        self.client_config = {
            "nickname": inputs[0].get_string(),
            "password": inputs[1].get_string(),
            "remember_password": self.client_config["remember_password"],
        }
        # response = requests.post(url, json=user_data)

        # if response.status_code == 200:
        pygame.mixer.fadeout(5000)
        pygame.quit()
        self.vpn_client = SoftEtherClient("Kaczk0vsky")
        # self.vpn_client = SoftEtherClient(user_data["nickname"])
        self.vpn_client.set_vpn_state(state=True)
        save_login_information(self.client_config)
        lobby = H5_Lobby(self.vpn_client)
        lobby.run_game()

        # self._window_overlay = True
        # self._wrong_password_status = True

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
