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
    """

    __id = 0
    _instances = []
    _tab_pressed = False
    _enter_pressed = False
    _backspace_pressed = False
    _time_constant = 100

    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        text_color: pygame.Color = pygame.Color("black"),
        fill_inactive: pygame.Color = pygame.Color("gray"),
        fill_active: pygame.Color = pygame.Color("white"),
        font_size: int = 20,
        text: str = "",
        is_active: bool = False,
        hide_text: bool = False,
    ):
        self.id = TextInput.__id
        self.rect = pygame.Rect(position[0], position[1], dimensions[0], dimensions[1])
        self.text_color = text_color
        self.fill_inactive = fill_inactive
        self.fill_active = fill_active
        self.hide_text = hide_text
        self.hidden_text = text
        self.text = text
        self.font = pygame.font.Font("resources/ASansrounded.ttf", font_size)
        self.txt_surface = self.font.render(
            len(self.text) * "*" if self.hide_text else self.text,
            True,
            self.text_color,
        )
        self.active = is_active
        self.last_backspace_time = 0

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
                    TextInput._enter_pressed = True
                elif event.key == pygame.K_ESCAPE:
                    self.active = False
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
                for instance in TextInput._instances:
                    instance._tab_pressed = False
                    TextInput._enter_pressed = False

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
            if current_time - self.last_backspace_time > TextInput._time_constant:
                if self.text:
                    self.text = self.text[:-1]
                    if self.hidden_text:
                        self.hidden_text = self.hidden_text[:-1]
                    self.txt_surface = self.font.render(
                        len(self.text) * "*" if self.hide_text else self.text,
                        True,
                        self.text_color,
                    )
                self.last_backspace_time = current_time

    def draw(self, screen: pygame.Surface) -> None:
        fill_color = self.fill_active if self.active else self.fill_inactive
        pygame.draw.rect(screen, fill_color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.text_color, self.rect, 2)

    def jump_to_next_input(self) -> None:
        self.active = False
        self._tab_pressed = False
        next_id = self.id + 1

        next_instance = None
        for instance in TextInput._instances:
            if instance.id == next_id:
                next_instance = instance
                break
        if not next_instance:
            next_instance = TextInput._instances[0]

        next_instance.active = True
        next_instance._tab_pressed = True

    def set_active(self, screen: pygame.Surface) -> None:
        self.active = True
        self.draw(screen)
