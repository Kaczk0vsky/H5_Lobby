import pygame
import os
import sys
import requests

from src.global_vars import fonts_sizes, bg_sound_volume, env_dict
from src.basic_window import BasicWindow
from src.lobby import H5_Lobby
from src.helpers import delete_objects, send_email
from src.vpn_handling import SoftEtherClient
from src.settings_reader import load_client_settings
from src.settings_writer import save_login_information
from widgets.text_input import TextInput
from widgets.button import Button
from widgets.check_box import CheckBox


class LoginWindow(BasicWindow):
    _window_overlay = False
    _wrong_credentials_status = False

    def __init__(self):
        BasicWindow.__init__(self)

        self.text_pos = [265, 260]
        self.buttons_pos = [400, 420]
        self.buttons_dims = (210, 60)
        self.long_buttons_dims = (310, 60)
        self.input_pos = [380, 240]
        self.input_dims = (200, 40)
        self.transformation_option = "800x600"
        self.font_size = fonts_sizes[self.transformation_option]

        self.client_config = load_client_settings()
        self.set_window_caption(title="Login")
        self.play_background_music(music_path="resources/H5_login_menu_theme.mp3")
        self.create_window_elements()

        self.SCREEN = pygame.display.set_mode((800, 600))
        self.BG = pygame.transform.scale(
            self.BG,
            (800, 600),
        )

    def login_window(self):
        self.BUTTON = pygame.transform.scale(self.BUTTON, self.buttons_dims)
        self.BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.BUTTON_HIGHLIGHTED, self.buttons_dims
        )
        self.LONG_BUTTON = pygame.transform.scale(self.BUTTON, self.long_buttons_dims)
        self.LONG_BUTTON_HIGHLIGHTED = pygame.transform.scale(
            self.BUTTON_HIGHLIGHTED, self.long_buttons_dims
        )
        CHECK_BOX_PASSWORD = CheckBox(
            surface=self.SCREEN,
            position=(self.SCREEN.get_width() / 1.7, self.SCREEN.get_height() / 1.675),
            dimensions=(20, 20),
            checked=self.client_config["remember_password"],
        )
        LOGIN_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1]),
            dimensions=self.input_dims,
            text=(
                self.client_config["nickname"]
                if self.client_config["remember_password"]
                else ""
            ),
            is_active=True,
        )
        PASSWORD_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] + 60),
            dimensions=self.input_dims,
            text=(
                self.client_config["password"]
                if self.client_config["remember_password"]
                else ""
            ),
        )
        INPUT_BOXES = [LOGIN_INPUT, PASSWORD_INPUT]
        HIDE_INPUT = [False, True]

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            LOGIN_TEXT = self.get_font(self.font_size[0]).render(
                "Username:", True, self.text_color
            )
            LOGIN_RECT = LOGIN_TEXT.get_rect(
                center=(self.text_pos[0], self.text_pos[1])
            )
            PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Password:", True, self.text_color
            )
            PASSWORD_RECT = PASSWORD_TEXT.get_rect(
                center=(self.text_pos[0], self.text_pos[1] + 60)
            )
            REMEMBER_LOGIN_TEXT = self.get_font(self.font_size[0]).render(
                "Remeber me:", True, self.text_color
            )
            REMEMBER_LOGIN_RECT = REMEMBER_LOGIN_TEXT.get_rect(
                center=(self.text_pos[0] + 100, self.text_pos[1] + 105)
            )

            self.SCREEN.blit(LOGIN_TEXT, LOGIN_RECT)
            self.SCREEN.blit(PASSWORD_TEXT, PASSWORD_RECT)
            self.SCREEN.blit(REMEMBER_LOGIN_TEXT, REMEMBER_LOGIN_RECT)

            LOGIN_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(self.buttons_pos[0], self.buttons_pos[1]),
                text_input="Login",
                font=self.get_font(font_size=30),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
            )

            REGISTER_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(self.buttons_pos[0], self.buttons_pos[1] + 65),
                text_input="Register",
                font=self.get_font(font_size=30),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
            )

            FORGOT_PASSWORD_BUTTON = Button(
                image=self.LONG_BUTTON,
                image_highlited=self.LONG_BUTTON_HIGHLIGHTED,
                pos=(self.buttons_pos[0], self.buttons_pos[1] + 130),
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
                        if LOGIN_BUTTON.check_for_input(MENU_MOUSE_POS):
                            self.login_player(INPUT_BOXES)
                        if REGISTER_BUTTON.check_for_input(MENU_MOUSE_POS):
                            delete_objects(INPUT_BOXES)
                            self.register_player()
                        if FORGOT_PASSWORD_BUTTON.check_for_input(MENU_MOUSE_POS):
                            delete_objects(INPUT_BOXES)
                            self.forgot_password_window()
                            self._window_overlay = True
                        if CHECK_BOX_PASSWORD.check_for_input(MENU_MOUSE_POS):
                            self.client_config["remember_password"] = (
                                not self.client_config["remember_password"]
                            )
                    else:
                        if self._wrong_credentials_status:
                            if BACK_BUTTON.check_for_input(MENU_MOUSE_POS):
                                self._window_overlay = False
                                LOGIN_INPUT.set_active(self.SCREEN)

            if not self._window_overlay:
                buttons = [LOGIN_BUTTON, REGISTER_BUTTON, FORGOT_PASSWORD_BUTTON]

                CHECK_BOX_PASSWORD.update()
                for button in buttons:
                    button.change_color(MENU_MOUSE_POS)
                    button.update(self.SCREEN, MENU_MOUSE_POS)
                for input in INPUT_BOXES:
                    input.update()
                    input.draw(self.SCREEN)

            if self._wrong_credentials_status:
                (WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT, BACK_BUTTON) = (
                    self.error_window(text="Given password is not correct!")
                )

                self.SCREEN.blit(self.SMALLER_WINDOWS_BG, (100, 100))
                self.SCREEN.blit(WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT)
                BACK_BUTTON.change_color(MENU_MOUSE_POS)
                BACK_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)

            pygame.display.update()

    def register_player(self):
        NICKNAME_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] - 110),
            dimensions=self.input_dims,
            is_active=True,
        )
        PASSWORD_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] - 60),
            dimensions=self.input_dims,
        )
        REPEAT_PASSWORD_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] - 10),
            dimensions=self.input_dims,
        )
        EMAIL_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] + 40),
            dimensions=self.input_dims,
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
                center=(self.text_pos[0], self.text_pos[1] - 110)
            )
            PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Password", True, self.text_color
            )
            PASSWORD_RECT = PASSWORD_TEXT.get_rect(
                center=(self.text_pos[0], self.text_pos[1] - 60)
            )
            REPEAT_PASSWORD_TEXT = self.get_font(self.font_size[0]).render(
                "Repeat Password", True, self.text_color
            )
            REPEAT_PASSWORD_RECT = REPEAT_PASSWORD_TEXT.get_rect(
                center=(self.text_pos[0], self.text_pos[1] - 10)
            )
            EMAIL_TEXT = self.get_font(self.font_size[0]).render(
                "Email", True, self.text_color
            )
            EMAIL_RECT = PASSWORD_TEXT.get_rect(
                center=(self.text_pos[0], self.text_pos[1] + 40)
            )

            self.SCREEN.blit(NICKNAME_TEXT, NICKNAME_RECT)
            self.SCREEN.blit(PASSWORD_TEXT, PASSWORD_RECT)
            self.SCREEN.blit(REPEAT_PASSWORD_TEXT, REPEAT_PASSWORD_RECT)
            self.SCREEN.blit(EMAIL_TEXT, EMAIL_RECT)

            REGISTER_ACCOUNT_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(self.buttons_pos[0], self.buttons_pos[1]),
                text_input="Submit",
                font=self.get_font(font_size=30),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
            )

            BACK_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(self.buttons_pos[0], self.buttons_pos[1] + 65),
                text_input="Back",
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
                        if_succesfull = self.register_new_player(INPUT_BOXES)
                        if if_succesfull:
                            delete_objects(INPUT_BOXES)
                            self.login_window()
                        else:
                            self._window_overlay = True
                            self._wrong_credentials_status = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self._window_overlay:
                        if REGISTER_ACCOUNT_BUTTON.check_for_input(MENU_MOUSE_POS):
                            if_succesfull = self.register_new_player(INPUT_BOXES)
                            if if_succesfull:
                                delete_objects(INPUT_BOXES)
                                self.login_window()
                            else:
                                self._window_overlay = True
                                self._wrong_credentials_status = True
                        elif BACK_BUTTON.check_for_input(MENU_MOUSE_POS):
                            delete_objects(INPUT_BOXES)
                            self.login_window()
                    else:
                        if self._wrong_credentials_status:
                            if RETURN_BUTTON.check_for_input(MENU_MOUSE_POS):
                                self._window_overlay = False
                                self._wrong_credentials_status = False
                                NICKNAME_INPUT.set_active(self.SCREEN)

            if not self._window_overlay:
                REGISTER_ACCOUNT_BUTTON.change_color(MENU_MOUSE_POS)
                REGISTER_ACCOUNT_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)
                BACK_BUTTON.change_color(MENU_MOUSE_POS)
                BACK_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)
                for input in INPUT_BOXES:
                    input.update()
                    input.draw(self.SCREEN)

            if self._wrong_credentials_status:
                (WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT, RETURN_BUTTON) = (
                    self.error_window(text="Username and Email already taken!")
                )

                self.SCREEN.blit(self.SMALLER_WINDOWS_BG, (100, 100))
                self.SCREEN.blit(WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT)
                RETURN_BUTTON.change_color(MENU_MOUSE_POS)
                RETURN_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)

            pygame.display.update()

    def forgot_password_window(self):
        NICKNAME_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1]),
            dimensions=self.input_dims,
            is_active=True,
        )
        EMAIL_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] + 65),
            dimensions=self.input_dims,
        )
        INPUT_BOXES = [
            NICKNAME_INPUT,
            EMAIL_INPUT,
        ]
        HIDE_INPUT = [False, False]

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            NICKNAME_TEXT = self.get_font(self.font_size[0]).render(
                "Username:", True, self.text_color
            )
            NICKNAME_RECT = NICKNAME_TEXT.get_rect(
                center=(self.text_pos[0], self.text_pos[1])
            )
            EMAIL_TEXT = self.get_font(self.font_size[0]).render(
                "Email:", True, self.text_color
            )
            EMAIL_RECT = EMAIL_TEXT.get_rect(
                center=(self.text_pos[0], self.text_pos[1] + 60)
            )
            self.SCREEN.blit(NICKNAME_TEXT, NICKNAME_RECT)
            self.SCREEN.blit(EMAIL_TEXT, EMAIL_RECT)

            SUBMIT_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(self.buttons_pos[0], self.buttons_pos[1]),
                text_input="Submit",
                font=self.get_font(font_size=30),
                base_color=self.text_color,
                hovering_color=self.hovering_color,
            )

            BACK_BUTTON = Button(
                image=self.BUTTON,
                image_highlited=self.BUTTON_HIGHLIGHTED,
                pos=(self.buttons_pos[0], self.buttons_pos[1] + 65),
                text_input="Back",
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
                        if_succesfull = self.set_new_password(INPUT_BOXES)
                        if if_succesfull:
                            delete_objects(INPUT_BOXES)
                            self.login_window()
                        else:
                            self._window_overlay = True
                            self._wrong_credentials_status = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self._window_overlay:
                        if SUBMIT_BUTTON.check_for_input(MENU_MOUSE_POS):
                            if_succesfull = self.set_new_password(INPUT_BOXES)
                            if if_succesfull:
                                delete_objects(INPUT_BOXES)
                                self.login_window()
                            else:
                                self._window_overlay = True
                                self._wrong_credentials_status = True
                        if BACK_BUTTON.check_for_input(MENU_MOUSE_POS):
                            delete_objects(INPUT_BOXES)
                            self.login_window()
                    else:
                        if self._wrong_credentials_status:
                            if RETURN_BUTTON.check_for_input(MENU_MOUSE_POS):
                                self._window_overlay = False
                                self._wrong_credentials_status = False
                                NICKNAME_INPUT.set_active(self.SCREEN)

            if not self._window_overlay:
                BACK_BUTTON.change_color(MENU_MOUSE_POS)
                BACK_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)
                SUBMIT_BUTTON.change_color(MENU_MOUSE_POS)
                SUBMIT_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)
                for input in INPUT_BOXES:
                    input.update()
                    input.draw(self.SCREEN)

            if self._wrong_credentials_status:
                (WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT, RETURN_BUTTON) = (
                    self.error_window(text="Given Username and Email do not match!")
                )

                self.SCREEN.blit(self.SMALLER_WINDOWS_BG, (100, 100))
                self.SCREEN.blit(WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT)
                RETURN_BUTTON.change_color(MENU_MOUSE_POS)
                RETURN_BUTTON.update(self.SCREEN, MENU_MOUSE_POS)

            pygame.display.update()

    def login_player(self, inputs: list):
        url = f"http://{env_dict["SERVER_URL"]}:8000/login/"
        self.client_config = {
            "nickname": inputs[0].get_string(),
            "password": inputs[1].get_string(),
            "remember_password": self.client_config["remember_password"],
        }
        response = requests.post(url, json=self.client_config)

        if response.status_code == 200:
            save_login_information(self.client_config)
            self.stop_background_music()
            if not self.vpn_client:
                self.vpn_client = SoftEtherClient(
                    self.client_config["nickname"],
                    self.client_config["password"],
                )
            self.vpn_client.set_vpn_state(state=True)
            lobby = H5_Lobby(self.vpn_client)
            lobby.run_game()

        self._window_overlay = True
        self._wrong_password_status = True

    def register_new_player(self, inputs: list):
        url = f"http://{env_dict["SERVER_URL"]}:8000/register/"
        user_data = {
            "nickname": inputs[0].get_string(),
            "password": inputs[1].get_string(),
            "repeat_password": inputs[2].get_string(),
            "email": inputs[3].get_string(),
        }

        # TODO: check if the useres already exists and email is free
        pass

        if user_data["password"] != user_data["repeat_password"]:
            # TODO: passwords do not match handling
            return False

        if len(user_data["password"]) < 8:
            # TODO: special conditions for password
            return False

        # TODO: check for nickname special conditions
        pass

        self.client_config = {
            "nickname": user_data["nickname"],
            "password": user_data["password"],
            "remember_password": False,
        }

        headers = {"Content-Type": "application/json"}
        data = requests.get(url)
        response = requests.post(url, json=user_data, headers=headers)
        if response.status_code == 200:
            data = data.json()
            self.vpn_client = SoftEtherClient(
                self.client_config["nickname"],
                self.client_config["password"],
            )
            is_succesfull = self.vpn_client.create_new_client()
            if is_succesfull:
                return True
        return False

    def set_new_password(self, inputs: list):
        user_data = {
            "nickname": inputs[0].get_string(),
            "email": inputs[1].get_string(),
        }

        # TODO: check if username and email exist in database in this combination
        pass

        is_sent = send_email(user_data)

        if is_sent:
            return True
        return False

    def run_game(self):
        self.login_window()
