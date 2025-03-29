import pygame

from src.helpers import play_on_empty


class CheckBox:
    """
    A class for creating a CheckBox.

    Attributes:
        surface (pygame.Surface): The surface on which the checkbox will be drawn.
        position (tuple[int, int]): The (x, y) position of the checkbox.
        dimensions (tuple[int, int]): The width and height of the checkbox.
        state (bool): The initial state of the checkbox (checked or unchecked).

    Methods:
        draw():
            Draws an empty checkbox on the selected surface.

        update():
            Changes the state if clicked. Draws an 'X' with black lines inside
            or an empty white background.

        check_for_input():
            Checks if a mouse click was detected inside the checkbox borders.
    """

    def __init__(
        self,
        surface: pygame.Surface,
        position: tuple[float, float],
        image: pygame.Surface,
        image_checked: pygame.Surface,
        checked: bool = False,
    ):
        self.surface = surface
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.image = image
        self.image_checked = image_checked
        self.checked = checked
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.is_active = False

    def update(self) -> None:
        if self.checked:
            self.surface.blit(self.image_checked, self.rect)
        else:
            self.surface.blit(self.image, self.rect)

    def check_for_input(self, position: tuple[int, int]) -> bool:
        if position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom):
            self.channel_index = play_on_empty("resources/button_click.mp3")
            self.checked = not self.checked
            self.is_active = True
            return True
        self.is_active = False
        return False
