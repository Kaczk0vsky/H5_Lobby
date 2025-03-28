import pygame

from src.helpers import play_on_empty


class Button:
    """
    A class for creating a Button.

    Attributes:
        image (pygame.Surface): The default image of the button.
        image_highlighted (pygame.Surface): The highlighted version of the button image.
        x_pos (float): The x-coordinate of the buttons position.
        y_pos (float): The y-coordinate of the buttons position.
        font (pygame.font.Font): The font used for the buttons text.
        base_color (str): The default text color.
        hovering_color (str): The text color when hovered over.
        text_input (str): The text displayed inside the button.
        text (pygame.Surface): The rendered text surface.
        rect (pygame.Rect): The rectangle defining the buttons position and size.
        text_rect (pygame.Rect): The rectangle defining the texts position and size.
        channel_index (int): The audio channel index for playing button sounds.

    Methods:
        update(screen: pygame.Surface, position: tuple[int, int]) -> None:
            Updates the buttons appearance based on the mouse position and draws it on the screen.

        check_for_input(position: tuple[int, int]) -> bool:
            Checks if the button was clicked and plays a click sound if clicked.

        change_color(position: tuple[int, int]) -> None:
            Changes the button's text color when the mouse hovers over it.

        handle_button(screen: pygame.Surface, position: tuple[int, int]) -> None:
            Combines `change_color` and `update` to handle button appearance changes.
    """

    def __init__(
        self,
        image: pygame.Surface,
        image_highlited: pygame.Surface,
        pos: tuple[float, float],
        font: pygame.font.Font,
        base_color: str,
        hovering_color: str,
        text_input: str = "",
        image_inactive: pygame.Surface = None,
        inactive_color: str = None,
    ):
        self.image = image
        self.image_highlighted = image_highlited
        if image_inactive:
            self.image_inactive = image_inactive
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        if inactive_color:
            self.inactive_color = inactive_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        for index in range(0, 8):
            if not pygame.mixer.Channel(index).get_busy():
                self.channel_index = index
        self.active = True

    def update(self, screen: pygame.Surface, position: tuple[int, int]) -> None:
        if self.active:
            if position[0] in range(self.rect.left, self.rect.right) and position[
                1
            ] in range(self.rect.top, self.rect.bottom):
                if self.image_highlighted is not None:
                    screen.blit(self.image_highlighted, self.rect)
            else:
                if self.image is not None:
                    screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image_inactive, self.rect)
        screen.blit(self.text, self.text_rect)

    def check_for_input(self, position: tuple[int, int]) -> bool:
        if self.active:
            if position[0] in range(self.rect.left, self.rect.right) and position[
                1
            ] in range(self.rect.top, self.rect.bottom):
                self.channel_index = play_on_empty("resources/button_click.mp3")
                return True
            return False

    def change_color(self, position: tuple[int, int]) -> None:
        if self.active:
            if position[0] in range(self.rect.left, self.rect.right) and position[
                1
            ] in range(self.rect.top, self.rect.bottom):
                self.text = self.font.render(self.text_input, True, self.hovering_color)
            else:
                self.text = self.font.render(self.text_input, True, self.base_color)
        else:
            self.text = self.font.render(self.text_input, True, self.inactive_color)

    def handle_button(self, screen: pygame.Surface, position: tuple[int, int]) -> None:
        self.change_color(position=position)
        self.update(screen=screen, position=position)

    def set_active(self, is_active: bool = True) -> None:
        self.active = is_active
