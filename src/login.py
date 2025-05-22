import pygame
import requests
import time
import re

from src.global_vars import fonts_sizes, env_dict
from src.basic_window import GameWindowsBase
from src.lobby import H5_Lobby
from src.helpers import (
    delete_objects,
    send_email,
    calculate_time_passed,
    check_input_correctnes,
    check_server_connection,
    render_small_caps,
)
from src.vpn_handling import SoftEtherClient
from src.settings_reader import load_user
from src.settings_writer import save_login_information
from src.decorators import run_in_thread
from widgets.text_input import TextInput
from widgets.button import Button
from widgets.check_box import CheckBox
from widgets.hover_box import HoverBox


class LoginWindow(GameWindowsBase):
    """Represents the login window for user authentication.

    This class handles the user login process, registration, and password recovery.
    It manages UI elements like text inputs, buttons, and checkboxes, and communicates
    with the server for authentication.

    Methods:
        login_window(): Displays the login UI and handles user interactions.
        register_player_window():  Displays the register UI and handles user interactions.
        forgot_password_window():  Displays the forgot password UI and handles user interactions.
        login_player(inputs: list): Send the request for authentication of the user to the server.
        If succesfull creates a VPN client class and H5_Lobby class.
        register_new_player(inputs: list): Registers a new user account and sends request to the server.
        set_new_password(inputs: list): Sends a password reset request.
        run_game(): Starts the main UI called in login_window().
    """

    __window_overlay = False
    __remove_all_widgets = False
    __allow_login = False
    __show_hint = False
    __show_nickname_hint = False
    __show_password_hint = False
    __server_unreachable = False
    __connection_timer = None
    __error_msg = None

    def __init__(self):
        GameWindowsBase.__init__(self)

        self.text_pos = [370, 275]
        self.buttons_pos = [400, 340]
        self.buttons_dims = (210, 60)
        self.input_pos = [250, 110]
        self.input_dims = (300, 50)
        self.hoverbox_pos = [565, 115]
        self.hoverbox_dims = (30, 40)
        self.checkbox_pos = [470, 275]
        self.checkbox_dims = (30, 30)
        self.error_window_dims = (600, 400)
        self.bg_dims = (800, 600)
        self.transformation_option = "800x600"
        self.font_size = fonts_sizes[self.transformation_option]

        if not check_server_connection():
            self.__server_unreachable = True
            self.__window_overlay = True
            self.__error_msg = "Server unreachable. Visit ToA Discord for more information."

        self.user = load_user()
        self.set_window_caption(title="Login")
        self.play_background_music(music_path="resources/H5_login_menu_theme.mp3")
        self.create_login_elements()

        self.SCREEN = pygame.display.set_mode(self.bg_dims, pygame.NOFRAME)
        self.BG = pygame.transform.scale(self.BG, self.bg_dims)

        self.session = requests.Session()
        self.csrf_token = None

    def login_window(self):
        self.BUTTON = pygame.transform.scale(self.BUTTON, self.buttons_dims)
        self.BUTTON_HIGHLIGHTED = pygame.transform.scale(self.BUTTON_HIGHLIGHTED, self.buttons_dims)
        self.BUTTON_INACTIVE = pygame.transform.scale(self.BUTTON, self.buttons_dims)
        self.LONG_BUTTON = pygame.transform.scale(self.BUTTON, self.buttons_dims)
        self.LONG_BUTTON_HIGHLIGHTED = pygame.transform.scale(self.BUTTON_HIGHLIGHTED, self.buttons_dims)
        self.QUESTION_MARK = pygame.transform.scale(self.QUESTION_MARK, self.hoverbox_dims)
        self.QUESTION_MARK_HIGHLIGHTED = pygame.transform.scale(self.QUESTION_MARK_HIGHLIGHTED, self.hoverbox_dims)
        self.TEXT_INPUT = pygame.transform.scale(self.TEXT_INPUT, self.input_dims)
        self.TEXT_BG = pygame.transform.scale(self.TEXT_BG, (400, 500))
        self.CHECKBOX = pygame.transform.scale(self.CHECKBOX, self.checkbox_dims)
        self.CHECKBOX_CHECKED = pygame.transform.scale(self.CHECKBOX_CHECKED, self.checkbox_dims)
        self.QUIT = pygame.transform.scale(self.QUIT, self.checkbox_dims)
        self.QUIT_HIGHLIGHTED = pygame.transform.scale(self.QUIT_HIGHLIGHTED, self.checkbox_dims)

        REMEMBER_LOGIN_TEXT = render_small_caps("Remeber me:", self.font_size[0], self.text_color)
        REMEMBER_LOGIN_RECT = REMEMBER_LOGIN_TEXT.get_rect(center=(self.text_pos[0], self.text_pos[1]))
        LOGIN_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            image_inactive=self.BUTTON_INACTIVE,
            position=(self.buttons_pos[0], self.buttons_pos[1]),
            text_input="Sign In",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )
        REGISTER_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            image_inactive=self.BUTTON_INACTIVE,
            position=(self.buttons_pos[0], self.buttons_pos[1] + 65),
            text_input="Sing Up",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )
        FORGOT_PASSWORD_BUTTON = Button(
            image=self.LONG_BUTTON,
            image_highlited=self.LONG_BUTTON_HIGHLIGHTED,
            image_inactive=self.BUTTON_INACTIVE,
            position=(self.buttons_pos[0], self.buttons_pos[1] + 130),
            text_input="Forgot Password?",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
            inactive_color=self.inactive_color,
        )
        if self.__server_unreachable:
            LOGIN_BUTTON.set_active(False)
            REGISTER_BUTTON.set_active(False)
            FORGOT_PASSWORD_BUTTON.set_active(False)

        QUIT_BUTTON = Button(
            image=self.QUIT,
            image_highlited=self.QUIT_HIGHLIGHTED,
            position=(550, 95),
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        CHECK_BOX_PASSWORD = CheckBox(
            position=(self.checkbox_pos[0], self.checkbox_pos[1]),
            image=self.CHECKBOX,
            image_checked=self.CHECKBOX_CHECKED,
            checked=self.user["remember_password"],
        )
        LOGIN_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1]),
            dimensions=self.input_dims,
            image=self.TEXT_INPUT,
            title="Username",
            text_color=self.text_color,
            font_size=self.font_size[0],
            font_title_size=self.font_size[1],
            text=(self.user["nickname"] if self.user["remember_password"] else ""),
            is_active=True,
        )
        PASSWORD_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] + 80),
            dimensions=self.input_dims,
            image=self.TEXT_INPUT,
            title="Password",
            text_color=self.text_color,
            font_size=self.font_size[0],
            font_title_size=self.font_size[1],
            text=(self.user["password"] if self.user["remember_password"] else ""),
            hide_text=True,
        )
        INPUT_BOXES = [LOGIN_INPUT, PASSWORD_INPUT]

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            self.SCREEN.blit(self.TEXT_BG, (200, 50))
            self.SCREEN.blit(REMEMBER_LOGIN_TEXT, REMEMBER_LOGIN_RECT)
            self.cursor.update()
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    self.quit_game_handling()
                for input in INPUT_BOXES:
                    input.event(event)
                    if input._enter_pressed == True and input.active:
                        self.__error_msg = self.login_player(INPUT_BOXES).join()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.__window_overlay:
                        if LOGIN_BUTTON.check_for_input(MENU_MOUSE_POS):
                            self.__error_msg = self.login_player(INPUT_BOXES).join()
                        if REGISTER_BUTTON.check_for_input(MENU_MOUSE_POS):
                            delete_objects(INPUT_BOXES)
                            self.register_player_window()
                        if FORGOT_PASSWORD_BUTTON.check_for_input(MENU_MOUSE_POS):
                            delete_objects(INPUT_BOXES)
                            self.forgot_password_window()
                            self.__window_overlay = True
                        if QUIT_BUTTON.check_for_input(MENU_MOUSE_POS):
                            self.quit_game_handling()
                        if CHECK_BOX_PASSWORD.check_for_input(MENU_MOUSE_POS):
                            self.user["remember_password"] = not self.user["remember_password"]
                    else:
                        if self.__error_msg:
                            if BACK_BUTTON.check_for_input(MENU_MOUSE_POS):
                                self.__window_overlay = False
                                self.__error_msg = None
                                LOGIN_INPUT.set_active(self.SCREEN)

            if not self.__window_overlay:
                CHECK_BOX_PASSWORD.update(self.SCREEN)
                LOGIN_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)
                REGISTER_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)
                FORGOT_PASSWORD_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)
                QUIT_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)

                for input in INPUT_BOXES:
                    input.update()
                    input.draw(self.SCREEN)

            if self.__connection_timer:
                time_passed = calculate_time_passed(start_time=self.__connection_timer)[1]
                if time_passed >= 3:
                    self.__window_overlay = True
                    self.__error_msg = f"Connecting for {time_passed} seconds..."

            if self.__error_msg:
                (WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT, BACK_BUTTON) = self.error_window(text=self.__error_msg, dimensions=self.error_window_dims)

                self.SCREEN.blit(self.SMALLER_WINDOWS_BG, (100, 100))
                self.SCREEN.blit(WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT)
                if not self.__connection_timer:
                    BACK_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)

            if self.__allow_login:
                self.__allow_login = False
                self.run_lobby()

            pygame.display.update()

    def register_player_window(self):
        self.CHECK_MARK = pygame.transform.scale(self.CHECK_MARK, self.checkbox_dims)
        self.UNCHECK_MARK = pygame.transform.scale(self.UNCHECK_MARK, self.checkbox_dims)

        nickname_dict = {
            0: [False, "Nickname requirements:"],
            1: [False, "Must be in between of 3 - 16 characters"],
            2: [False, "Only small/big letters or numbers"],
        }
        password_dict = {
            0: [False, "Password requirements:"],
            1: [False, "Must be longer than 8 characters"],
            2: [False, "Must contain one small and big letter"],
            3: [False, "Must contain one of special characters: !^#+$=%"],
            4: [False, "Passwords must be the same"],
        }

        REGISTER_ACCOUNT_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(self.buttons_pos[0], self.buttons_pos[1] + 65),
            text_input="Submit",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        BACK_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(self.buttons_pos[0], self.buttons_pos[1] + 130),
            text_input="Back",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        HOVER_BOX_NICKNAME = HoverBox(
            image=self.QUESTION_MARK,
            image_highlited=self.QUESTION_MARK_HIGHLIGHTED,
            position=(self.hoverbox_pos[0], self.hoverbox_pos[1]),
        )
        HOVER_BOX_PASSWORD = HoverBox(
            image=self.QUESTION_MARK,
            image_highlited=self.QUESTION_MARK_HIGHLIGHTED,
            position=(self.hoverbox_pos[0], self.hoverbox_pos[1] + 65),
        )
        NICKNAME_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] - 20),
            dimensions=self.input_dims,
            image=self.TEXT_INPUT,
            title="Username",
            text_color=self.text_color,
            font_size=self.font_size[0],
            font_title_size=self.font_size[1],
            is_active=True,
        )
        PASSWORD_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] + 45),
            dimensions=self.input_dims,
            image=self.TEXT_INPUT,
            title="Password",
            text_color=self.text_color,
            font_size=self.font_size[0],
            font_title_size=self.font_size[1],
            hide_text=True,
        )
        REPEAT_PASSWORD_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] + 110),
            dimensions=self.input_dims,
            image=self.TEXT_INPUT,
            title="Repeat Password",
            text_color=self.text_color,
            font_size=self.font_size[0],
            font_title_size=self.font_size[1],
            hide_text=True,
        )
        EMAIL_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] + 175),
            dimensions=self.input_dims,
            image=self.TEXT_INPUT,
            title="Email",
            text_color=self.text_color,
            font_size=self.font_size[0],
            font_title_size=self.font_size[1],
        )
        INPUT_BOXES = [
            NICKNAME_INPUT,
            PASSWORD_INPUT,
            REPEAT_PASSWORD_INPUT,
            EMAIL_INPUT,
        ]

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            self.SCREEN.blit(self.TEXT_BG, (200, 50))
            self.cursor.update()
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    self.quit_game_handling()
                for input in INPUT_BOXES:
                    input.event(event)
                    if input._enter_pressed == True and input.active:
                        self.__error_msg = self.register_new_player(INPUT_BOXES).join()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.__window_overlay:
                        if REGISTER_ACCOUNT_BUTTON.check_for_input(MENU_MOUSE_POS):
                            self.__error_msg = self.register_new_player(INPUT_BOXES).join()
                        elif BACK_BUTTON.check_for_input(MENU_MOUSE_POS):
                            self.__remove_all_widgets = True
                        elif HOVER_BOX_NICKNAME.check_for_input(MENU_MOUSE_POS):
                            self.__show_hint = True
                            self.__show_nickname_hint = True
                        elif HOVER_BOX_PASSWORD.check_for_input(MENU_MOUSE_POS):
                            self.__show_hint = True
                            self.__show_password_hint = True
                    else:
                        if self.__error_msg:
                            if RETURN_BUTTON.check_for_input(MENU_MOUSE_POS):
                                self.__window_overlay = False
                                self.__error_msg = None

                        if self.__show_hint:
                            if RETURN_BUTTON.check_for_input(MENU_MOUSE_POS):
                                self.__window_overlay = False
                                self.__show_hint = False

                        NICKNAME_INPUT.set_active(self.SCREEN)

            if not self.__window_overlay or not self.__show_hint:
                REGISTER_ACCOUNT_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)
                BACK_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)
                HOVER_BOX_NICKNAME.update(self.SCREEN, MENU_MOUSE_POS)
                HOVER_BOX_PASSWORD.update(self.SCREEN, MENU_MOUSE_POS)
                for input in INPUT_BOXES:
                    input.update()
                    input.draw(self.SCREEN)

            if self.__connection_timer:
                time_passed = calculate_time_passed(start_time=self.__connection_timer)[1]
                if time_passed >= 3:
                    self.__window_overlay = True
                    self.__error_msg = f"Connecting for {time_passed} seconds..."

            if self.__error_msg:
                (WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT, RETURN_BUTTON) = self.error_window(
                    text=self.__error_msg, dimensions=self.error_window_dims
                )
                self.SCREEN.blit(self.SMALLER_WINDOWS_BG, (100, 100))
                self.SCREEN.blit(WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT)

                if not self.__connection_timer:
                    RETURN_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)

            if self.__show_hint:
                self.__window_overlay = True
                text_input_dict = None

                if self.__show_nickname_hint:
                    text_input_dict = check_input_correctnes(INPUT_BOXES, nickname_dict)
                    self.__show_nickname_hint = False

                if self.__show_password_hint:
                    text_input_dict = check_input_correctnes(INPUT_BOXES, password_dict)

                if text_input_dict:
                    RETURN_BUTTON = self.hints_window(text_input_dict)
                    self.__show_password_hint = False

                self.render_hints()
                RETURN_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)

            if self.__remove_all_widgets:
                self.__remove_all_widgets = False
                delete_objects(INPUT_BOXES)
                self.login_window()

            pygame.display.update()

    def forgot_password_window(self):
        SUBMIT_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(self.buttons_pos[0], self.buttons_pos[1]),
            text_input="Submit",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        BACK_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(self.buttons_pos[0], self.buttons_pos[1] + 65),
            text_input="Back",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        NICKNAME_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1]),
            dimensions=self.input_dims,
            image=self.TEXT_INPUT,
            title="Username",
            text_color=self.text_color,
            font_size=self.font_size[0],
            font_title_size=self.font_size[1],
            is_active=True,
        )
        EMAIL_INPUT = TextInput(
            position=(self.input_pos[0], self.input_pos[1] + 80),
            dimensions=self.input_dims,
            image=self.TEXT_INPUT,
            title="Email",
            text_color=self.text_color,
            font_size=self.font_size[0],
            font_title_size=self.font_size[1],
        )
        INPUT_BOXES = [
            NICKNAME_INPUT,
            EMAIL_INPUT,
        ]

        while True:
            self.SCREEN.blit(self.BG, (0, 0))
            self.SCREEN.blit(self.TEXT_BG, (200, 50))
            self.cursor.update()
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    self.quit_game_handling()
                for input in INPUT_BOXES:
                    input.event(event)
                    if input._enter_pressed == True and input.active:
                        self.__error_msg = self.set_new_password(INPUT_BOXES).join()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.__window_overlay:
                        if SUBMIT_BUTTON.check_for_input(MENU_MOUSE_POS):
                            self.__error_msg = self.set_new_password(INPUT_BOXES).join()
                        if BACK_BUTTON.check_for_input(MENU_MOUSE_POS):
                            self.__remove_all_widgets = True
                    else:
                        if self.__error_msg:
                            if RETURN_BUTTON.check_for_input(MENU_MOUSE_POS):
                                self.__window_overlay = False
                                self.__error_msg = None
                                NICKNAME_INPUT.set_active(self.SCREEN)

            if not self.__window_overlay:
                SUBMIT_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)
                BACK_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)
                for input in INPUT_BOXES:
                    input.update()
                    input.draw(self.SCREEN)

            if self.__connection_timer:
                time_passed = calculate_time_passed(start_time=self.__connection_timer)
                if time_passed[1] >= 3:
                    self.__window_overlay = True
                    self.__error_msg = f"Connecting for {time_passed[1]} seconds..."

            if self.__error_msg:
                (WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT, RETURN_BUTTON) = self.error_window(
                    text=self.__error_msg, dimensions=self.error_window_dims
                )
                self.SCREEN.blit(self.SMALLER_WINDOWS_BG, (100, 100))
                self.SCREEN.blit(WRONG_PASSWORD_TEXT, WRONG_PASSWORD_RECT)

                if not self.__connection_timer:
                    RETURN_BUTTON.handle_button(self.SCREEN, MENU_MOUSE_POS)

            if self.__remove_all_widgets:
                self.__remove_all_widgets = False
                delete_objects(INPUT_BOXES)
                self.login_window()

            pygame.display.update()

    def hints_window(self, text_input: dict[any, list]):
        self.check_list = []
        overlay_width, overlay_height = 600, 400
        x_pos, y_pos = 200, 150

        for key in text_input.keys():
            if text_input[key][0]:
                self.check_list.append(self.CHECK_MARK)
            else:
                self.check_list.append(self.UNCHECK_MARK)

        self.SMALLER_WINDOWS_BG = pygame.transform.scale(self.SMALLER_WINDOWS_BG, (overlay_width, overlay_height))

        self.TITLE_TEXT = render_small_caps(text_input[0][1], self.font_size[0], self.text_color)
        self.TITLE_RECT = self.TITLE_TEXT.get_rect(center=(x_pos * 2, y_pos))
        self.FIRST_TEXT = render_small_caps(text_input[1][1], self.font_size[0], self.text_color)
        self.FIRST_RECT = self.FIRST_TEXT.get_rect(topleft=(x_pos, y_pos + 50))
        self.SECOND_TEXT = render_small_caps(text_input[2][1], self.font_size[0], self.text_color)
        self.SECOND_RECT = self.SECOND_TEXT.get_rect(topleft=(x_pos, y_pos + 100))
        self.THIRD_TEXT = None
        self.THIRD_RECT = None
        self.FOURTH_TEXT = None
        self.FOURTH_RECT = None

        if self.__show_password_hint:
            self.THIRD_TEXT = render_small_caps(text_input[3][1], self.font_size[0], self.text_color)
            self.THIRD_RECT = self.THIRD_TEXT.get_rect(topleft=(x_pos, y_pos + 150))
            self.FOURTH_TEXT = render_small_caps(text_input[4][1], self.font_size[0], self.text_color)
            self.FOURTH_RECT = self.FOURTH_TEXT.get_rect(topleft=(x_pos, y_pos + 200))

        BACK_BUTTON = Button(
            image=self.BUTTON,
            image_highlited=self.BUTTON_HIGHLIGHTED,
            position=(400, 420),
            text_input="Back",
            font_size=self.font_size[1],
            base_color=self.text_color,
            hovering_color=self.hovering_color,
        )
        return BACK_BUTTON

    def render_hints(self):
        self.SCREEN.blit(self.SMALLER_WINDOWS_BG, (100, 100))
        self.SCREEN.blit(self.TITLE_TEXT, self.TITLE_RECT)
        self.SCREEN.blit(self.check_list[1], (self.FIRST_RECT.x - 50, self.FIRST_RECT.y))
        self.SCREEN.blit(self.FIRST_TEXT, self.FIRST_RECT)
        self.SCREEN.blit(self.check_list[2], (self.FIRST_RECT.x - 50, self.SECOND_RECT.y))
        self.SCREEN.blit(self.SECOND_TEXT, self.SECOND_RECT)

        if self.THIRD_TEXT and self.FOURTH_TEXT:
            self.SCREEN.blit(self.check_list[3], (self.FIRST_RECT.x - 50, self.THIRD_RECT.y))
            self.SCREEN.blit(self.THIRD_TEXT, self.THIRD_RECT)
            self.SCREEN.blit(self.FOURTH_TEXT, self.FOURTH_RECT)
            self.SCREEN.blit(self.check_list[4], (self.FIRST_RECT.x - 50, self.FOURTH_RECT.y))

    @run_in_thread
    def login_player(self, inputs: list):
        url = f"https://{env_dict['SERVER_URL']}/db/{env_dict['PATH_LOGIN']}/"
        user_data = {
            "nickname": inputs[0].get_string(),
            "password": inputs[1].get_string(),
            "remember_password": self.user["remember_password"],
        }

        if not user_data["nickname"] or not user_data["password"]:
            self.__window_overlay = True
            return "Fields cannot be empty!"

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", user_data["nickname"]):
            self.__window_overlay = True
            return "Nickname has incorrect format!"

        if not re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d#$%^+=!]{8,}$",
            user_data["password"],
        ):
            self.__window_overlay = True
            return "Passowrd has incorrect format!"

        if not self.csrf_token or "Error" in self.csrf_token:
            self.csrf_token = self.get_csrf_token()

        if "Error" in self.csrf_token:
            self.__window_overlay = True
            return self.csrf_token

        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.csrf_token,
            "Content-Type": "application/json",
        }
        self.session.cookies.set("csrftoken", self.csrf_token)
        try:
            response = self.session.post(url, json=user_data, headers=headers)
            if response.status_code == 200:
                save_login_information(user_data)
                if self.vpn_client is None:
                    self.vpn_client = SoftEtherClient(
                        user_data["nickname"],
                        user_data["password"],
                    )
                    self.vpn_client.create_new_client()
                self.vpn_client.set_vpn_state(state=True)
                self.__allow_login = True
                return None

            elif response.status_code == 400:
                self.__window_overlay = True
                return response.json().get("error", "Unknown error occurred")

        except requests.exceptions.ConnectTimeout:
            self.__window_overlay = True
            return "Error occured while trying to connect to server!"

        except requests.exceptions.ConnectionError:
            self.__window_overlay = True
            return "Error! Check your internet connection..."

        except:
            self.__window_overlay = True
            return "Error! Server/Player offline, check discord..."

    @run_in_thread
    def register_new_player(self, inputs: list):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict["PATH_REGISTER"]}/"
        user_data = {
            "nickname": inputs[0].get_string(),
            "password": inputs[1].get_string(),
            "repeat_password": inputs[2].get_string(),
            "email": inputs[3].get_string(),
        }

        if not all(user_data.values()):
            self.__window_overlay = True
            return "Fields cannot be empty!"

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", user_data["nickname"]):
            self.__window_overlay = True
            return "Nickname has incorrect format!"

        if not re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d#$%^+=!]{8,}$",
            user_data["password"],
        ):
            self.__window_overlay = True
            return "Password has incorrect format!"

        if user_data["password"] != user_data["repeat_password"]:
            self.__window_overlay = True
            return "Passwords do not match!"

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", user_data["email"]):
            self.__window_overlay = True
            return "Email has incorrect format!"

        if not self.csrf_token or "Error" in self.csrf_token:
            self.csrf_token = self.get_csrf_token()

        if "Error" in self.csrf_token:
            self.__window_overlay = True
            return self.csrf_token

        self.user = {
            "nickname": user_data["nickname"],
            "password": user_data["password"],
            "remember_password": False,
            "crsf_token": self.csrf_token,
        }
        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.csrf_token,
            "Content-Type": "application/json",
        }
        self.session.cookies.set("csrftoken", self.csrf_token)
        try:
            response = self.session.post(url, json=user_data, headers=headers)
            if response.status_code == 200:
                self.vpn_client = SoftEtherClient(
                    self.user["nickname"],
                    self.user["password"],
                )
                self.vpn_client.create_new_client()
                self.__remove_all_widgets = True
                return None

            elif response.status_code == 400:
                self.__window_overlay = True
                return response.json().get("error", "Unknown error occurred")

        except requests.exceptions.ConnectTimeout:
            self.__window_overlay = True
            return "Error occured while trying to connect to server!"

        except requests.exceptions.ConnectionError:
            self.__window_overlay = True
            return "Error! Check your internet connection..."

        except:
            self.__window_overlay = True
            return "Error! Server/Player offline, check discord..."

    @run_in_thread
    def set_new_password(self, inputs: list):
        url = f"https://{env_dict["SERVER_URL"]}/db/{env_dict['PATH_CHANGE_PASSWORD']}/"
        user_data = {
            "nickname": inputs[0].get_string(),
            "email": inputs[1].get_string(),
        }

        if not all(user_data.values()):
            self.__window_overlay = True
            return "Fields cannot be empty!"

        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", user_data["nickname"]):
            self.__window_overlay = True
            return "Nickname has incorrect format!"

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", user_data["email"]):
            self.__window_overlay = True
            return "Email has incorrect format!"

        if not self.csrf_token or "Error" in self.csrf_token:
            self.csrf_token = self.get_csrf_token()

        if "Error" in self.csrf_token:
            self.__window_overlay = True
            return self.csrf_token

        headers = {
            "Referer": "https://h5-tavern.pl/",
            "X-CSRFToken": self.csrf_token,
            "Content-Type": "application/json",
        }
        self.session.cookies.set("csrftoken", self.csrf_token)
        try:
            response = self.session.get(url, params=user_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                reset_url = data.get("reset_url")
                if send_email(user_data, reset_url):
                    self.__remove_all_widgets = True
                    self.__window_overlay = False
                    return None
                else:
                    self.__window_overlay = True
                    return "Error occured during sending email!"

            elif response.status_code == 400 or response.status_code == 404:
                self.__window_overlay = True
                return "User with this email doesn`t exist!"

        except requests.exceptions.ConnectTimeout:
            self.__window_overlay = True
            return "Error occured while trying to connect to server!"

        except requests.exceptions.ConnectionError:
            self.__window_overlay = True
            return "Error! Check your internet connection..."

        except:
            self.__window_overlay = True
            return "Error! Server/Player offline, check discord..."

    def get_csrf_token(self):
        url = f"https://{env_dict['SERVER_URL']}/db/{env_dict['PATH_TOKEN']}/"
        try:
            self.__connection_timer = time.time()
            self.__getting_token = True
            response = self.session.get(url)
            if response.status_code == 200:
                self.__getting_token = False
                self.__connection_timer = None
            if "csrftoken" in response.cookies:
                return response.cookies["csrftoken"]
            return None
        except requests.exceptions.ConnectTimeout:
            self.__window_overlay = True
            self.__error_msg = "Error occured while trying to connect to server!"

        except requests.exceptions.ConnectionError:
            self.__window_overlay = True
            self.__error_msg = "Error! Check your internet connection..."

        except:
            self.__window_overlay = True
            self.__error_msg = "Error! Server/Player offline, check discord..."

    def run_login(self):
        self.login_window()

    def run_lobby(self):
        self.stop_background_music()
        lobby = H5_Lobby(
            vpn_client=self.vpn_client,
            user=self.user,
            crsf_token=self.csrf_token,
            session=self.session,
        )
        lobby.run_game()
