import pygame

from src.helpers import play_on_empty


class CheckBox:
    """
    A class for creating an interactive checkbox in Pygame.

    Attributes:
        position (tuple[float, float]): The x and y coordinates of the checkbox.
        image (pygame.Surface): The default image of the checkbox.
        image_checked (pygame.Surface): The image displayed when the checkbox is checked.
        checked (bool, optional): The initial state of the checkbox (default: False).
        rect (pygame.Rect): The rectangle defining the checkbox's position and dimensions.
        is_active (bool): Whether the checkbox is currently active.

    Methods:
        update(screen: pygame.Surface) -> None:
            Draws the appropriate checkbox image based on its state.

        check_for_input(position: tuple[int, int]) -> bool:
            Checks if the checkbox was clicked and toggles its state accordingly.
            Plays a click sound effect when activated.
    """

    def __init__(
        self,
        position: tuple[float, float],
        image: pygame.Surface,
        image_checked: pygame.Surface,
        checked: bool = False,
    ):
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.image = image
        self.image_checked = image_checked
        self.checked = checked
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.is_active = False

    def update(self, screen: pygame.Surface) -> None:
        if self.checked:
            screen.blit(self.image_checked, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def check_for_input(self, position: tuple[int, int]) -> bool:
        if position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom):
            play_on_empty(path="resources/button_click.mp3")
            self.checked = not self.checked
            self.is_active = True
            return True
        self.is_active = False
        return False
