import pygame

from src.helpers import render_small_caps


class TextInput:
    """
    A class for creating interactive text input fields in Pygame.

    Attributes:
        position (tuple[float, float]): The x and y coordinates of the text input field.
        dimensions (tuple[int, int]): The width and height of the text input field.
        image (pygame.Surface): The background image of the text input field.
        title (str): The title displayed above the input field.
        text_color (pygame.Color): The color of the input text.
        font (pygame.font.Font): The font used for rendering the input text.
        font_title (pygame.font.Font): The font used for rendering the title.
        text_bg_color (pygame.Color, optional): The background color of the text area (default: "#1e2120").
        text (str, optional): The initial text inside the input field (default: "").
        is_active (bool, optional): Whether the input field is active (default: False).
        hide_text (bool, optional): Whether the input should be hidden (e.g., for passwords) (default: False).

    Methods:
        delete_instance() -> None:
            Removes the current instance from the list of active `TextInput` instances.

        event(event: pygame.event.Event) -> None:
            Handles user input events such as typing, clicking, and special key presses.

        get_string() -> str:
            Returns the input text, revealing hidden characters if used for passwords.

        update() -> None:
            Manages continuous backspace functionality based on timing constraints.

        draw(screen: pygame.Surface) -> None:
            Draws the input box and text on the given screen.

        set_active(screen: pygame.Surface) -> None:
            Activates the input field and redraws it on the screen.

        __jump_to_next_input() -> None:
            Switches focus to the next `TextInput` field when the Tab key is pressed.

        __update_text_surface() -> None:
            Adjusts the text rendering to ensure proper display within the field.
    """

    __id = 0
    _chars_deleted = 0
    _last_backspace_time = 0
    _scroll_offset = 0
    _time_constant = 100
    _tab_pressed = False
    _backspace_pressed = False
    _enter_pressed = False
    _instances = []

    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        image: pygame.Surface,
        title: str,
        text_color: pygame.Color,
        font_size: int,
        font_title_size: int,
        text_bg_color: pygame.Color = pygame.Color("#1e2120"),
        text: str = "",
        is_active: bool = False,
        hide_text: bool = False,
    ):
        self.id = TextInput.__id
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.w = dimensions[0]
        self.h = dimensions[1]
        self.image = image
        self.title = title
        self.text_color = text_color
        self.text_bg_color = text_bg_color
        self.active = is_active
        self.hide_text = hide_text
        self.hidden_text = text
        self.text = text
        self.font_size = font_size
        self.font_title_size = font_title_size
        self.rect = pygame.Rect(self.x_pos, self.y_pos, self.w, self.h)
        self.rect_bg = pygame.Rect(
            self.x_pos + 12.5,
            self.y_pos + 12.5,
            self.w - self.w * 0.085,
            self.h - self.h * 0.45,
        )
        self.txt_surface = render_small_caps(len(self.text) * "*" if self.hide_text else self.text, self.font_size, self.text_color)
        self.title_surface = render_small_caps(self.title, self.font_title_size, self.text_color)

        TextInput.__id += 1
        TextInput._instances.append(self)

    def delete_instance(self) -> None:
        if self in TextInput._instances:
            TextInput._instances.remove(self)

        if not TextInput._instances:
            TextInput.__id = 0

    def event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = False
            if self.rect.collidepoint(event.pos):
                self.active = True

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self._backspace_pressed = True
                elif event.key == pygame.K_TAB:
                    if not self._tab_pressed:
                        self.__jump_to_next_input()
                elif event.key == pygame.K_RETURN:
                    self._enter_pressed = True
                elif event.key == pygame.K_ESCAPE:
                    self.active = False
                elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_CAPSLOCK]:
                    pass
                elif len(self.text) < 24:
                    if self.hide_text:
                        self.text += "*"
                        self.hidden_text += event.unicode
                    else:
                        self.text += event.unicode

        if event.type == pygame.KEYUP:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self._backspace_pressed = False
                    self._chars_deleted = 0
                    self._time_constant = 100
                for instance in self._instances:
                    instance._tab_pressed = False
                    self._enter_pressed = False

        self.txt_surface = render_small_caps(len(self.text) * "*" if self.hide_text else self.text, self.font_size, self.text_color)

    def get_string(self) -> str:
        if len(self.text) == len(self.hidden_text):
            return self.hidden_text
        return self.text

    def update(self) -> None:
        current_time = pygame.time.get_ticks()
        if self.active and self._backspace_pressed:
            if current_time - self._last_backspace_time > self._time_constant:
                if self.text:
                    self._chars_deleted += 1
                    if self._chars_deleted == 5:
                        self._time_constant = 40
                    self.text = self.text[:-1]
                    if self.hidden_text:
                        self.hidden_text = self.hidden_text[:-1]
                    self.txt_surface = render_small_caps(len(self.text) * "*" if self.hide_text else self.text, self.font_size, self.text_color)
                self._last_backspace_time = current_time
        self.__update_text_surface()

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
        if self.active:
            pygame.draw.rect(screen, self.text_bg_color, self.rect_bg)

        text_width = self.txt_surface.get_width()
        text_x = self.rect_bg.x + (self.rect_bg.width - text_width) / 2

        text_surface_clipped = pygame.Surface((self.rect_bg.width, self.rect_bg.height), pygame.SRCALPHA)

        text_surface_clipped.blit(self.txt_surface, (0, 0))

        title_rect = self.title_surface.get_rect(center=(self.rect.x + self.rect.w / 2, self.rect.y - self.rect.h / 10))
        screen.blit(self.title_surface, title_rect.topleft)
        screen.blit(text_surface_clipped, (text_x, self.rect.y + 12.5))

    def set_active(self, screen: pygame.Surface) -> None:
        self.active = True
        self.draw(screen)

    def __jump_to_next_input(self) -> None:
        self.active = False
        self._tab_pressed = False
        next_id = self.id + 1

        next_instance = None
        for instance in self._instances:
            if instance.id == next_id:
                next_instance = instance
                break
        if not next_instance:
            next_instance = self._instances[0]

        next_instance.active = True
        next_instance._tab_pressed = True

    def __update_text_surface(self) -> None:
        text_width = self.txt_surface.get_width()
        if text_width > self.rect.width - 10:
            self._scroll_offset = text_width - (self.rect.width - 10)
        else:
            self._scroll_offset = 0
