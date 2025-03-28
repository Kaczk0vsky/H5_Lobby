import pygame


class TextInput:
    """
    A class for creating interactive text input fields in Pygame.

    Attributes:
        _id (int): A unique identifier for each instance.
        _instances (list[TextInput]): A list of all `TextInput` instances.
        _tab_pressed (bool): Tracks if the Tab key was pressed to switch input fields.
        _enter_pressed (bool): Tracks if the Enter key was pressed.
        _backspace_pressed (bool): Tracks if the Backspace key was held down.
        _time_constant (int): The delay (in milliseconds) for backspace repeat behavior.

        id (int): Unique ID for the instance.
        rect (pygame.Rect): The rectangular area representing the input box.
        text_color (pygame.Color): The color of the text.
        fill_inactive (pygame.Color): Background color when the field is inactive.
        fill_active (pygame.Color): Background color when the field is active.
        hidden_text (str): Stores the raw input (used when hiding text, e.g., password fields).
        text (str): The displayed text in the input box.
        FONT (pygame.font.Font): The font used for rendering text.
        txt_surface (pygame.Surface): The rendered text surface.
        active (bool): Determines whether the text input is currently active.
        last_backspace_time (int): Tracks the last recorded backspace press time.
        hide_text (bool): If true then the text input remains hidden.

    Methods:
        delete_instance() -> None:
            Removes the current instance from `_instances` and resets `_id` if no instances remain.

        event(event: pygame.event.Event) -> None:
            Handles user input events such as typing, clicking, and special key presses.

        get_string() -> str:
            Returns the input text, revealing hidden characters if used for passwords.

        update() -> None:
            Manages continuous backspace functionality based on `_time_constant`.

        draw(screen: pygame.Surface) -> None:
            Draws the input box on the given screen.

        jump_to_next_input() -> None:
            Switches focus to the next `TextInput` field when the Tab key is pressed.

        set_active(screen: pygame.Surface) -> None:
            Activates the input box and redraws it on the screen.

        update_text_surface() -> None:
            Calculates the offset value for the text render fucntion.
    """

    __id = 0
    _instances = []
    _tab_pressed = False
    _backspace_pressed = False
    _time_constant = 100
    _chars_deleted = 0

    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        image: pygame.Surface,
        title: str,
        text_color: pygame.Color,
        text_bg_color: pygame.Color = pygame.Color("#1e2120"),
        font_size: int = 20,
        font_size_title: int = 16,
        text: str = "",
        is_active: bool = False,
        hide_text: bool = False,
    ):
        self.id = TextInput.__id
        self.rect = pygame.Rect(position[0], position[1], dimensions[0], dimensions[1])
        self.rect_bg = pygame.Rect(
            position[0] + 12.5,
            position[1] + 12.5,
            dimensions[0] - dimensions[0] * 0.085,
            dimensions[1] - dimensions[1] * 0.45,
        )
        self.image = image
        self.title = title
        self.text_color = text_color
        self.text_bg_color = text_bg_color
        self.hide_text = hide_text
        self.hidden_text = text
        self.text = text
        self.font = pygame.font.Font("resources/ASansrounded.ttf", font_size)
        self.font_title = pygame.font.Font(
            "resources/ASansrounded.ttf", font_size_title
        )
        self.txt_surface = self.font.render(
            len(self.text) * "*" if self.hide_text else self.text,
            True,
            self.text_color,
        )
        self.title_surface = self.font_title.render(self.title, True, self.text_color)
        self.active = is_active
        self.last_backspace_time = 0
        self.scroll_offset = 0
        self.enter_pressed = False

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
                        self.jump_to_next_input()
                elif event.key == pygame.K_RETURN:
                    self.enter_pressed = True
                elif event.key == pygame.K_ESCAPE:
                    self.active = False
                elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_CAPSLOCK]:
                    pass
                else:
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
                    self.enter_pressed = False

        self.txt_surface = self.font.render(
            len(self.text) * "*" if self.hide_text else self.text,
            True,
            self.text_color,
        )

    def get_string(self) -> str:
        if len(self.text) == len(self.hidden_text):
            return self.hidden_text
        return self.text

    def update(self) -> None:
        current_time = pygame.time.get_ticks()
        if self.active and self._backspace_pressed:
            if current_time - self.last_backspace_time > self._time_constant:
                if self.text:
                    self._chars_deleted += 1
                    if self._chars_deleted == 5:
                        self._time_constant = 40
                    self.text = self.text[:-1]
                    if self.hidden_text:
                        self.hidden_text = self.hidden_text[:-1]
                    self.txt_surface = self.font.render(
                        len(self.text) * "*" if self.hide_text else self.text,
                        True,
                        self.text_color,
                    )
                self.last_backspace_time = current_time
        self.update_text_surface()

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
        if self.active:
            pygame.draw.rect(screen, self.text_bg_color, self.rect_bg)
        text_surface_clipped = pygame.Surface(
            (self.rect.width - 10, self.rect.height), pygame.SRCALPHA
        )
        text_surface_clipped.blit(self.txt_surface, (-self.scroll_offset, 0))
        title_rect = self.title_surface.get_rect(
            center=(self.rect.x + self.rect.w / 2, self.rect.y - self.rect.h / 10)
        )
        screen.blit(self.title_surface, title_rect.topleft)
        screen.blit(text_surface_clipped, (self.rect.x + 20, self.rect.y + 12.5))

    def jump_to_next_input(self) -> None:
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

    def set_active(self, screen: pygame.Surface) -> None:
        self.active = True
        self.draw(screen)

    def update_text_surface(self) -> None:
        text_width = self.txt_surface.get_width()
        if text_width > self.rect.width - 10:
            self.scroll_offset = text_width - (self.rect.width - 10)
        else:
            self.scroll_offset = 0
