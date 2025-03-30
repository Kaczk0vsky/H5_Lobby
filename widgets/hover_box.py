import pygame

from src.helpers import play_on_empty


class HoverBox:
    """
    A class for creating an interactive hoverable box in Pygame.

    Attributes:
        position (tuple[float, float]): The x and y coordinates of the hover box.
        image (pygame.Surface): The default image of the hover box.
        image_highlighted (pygame.Surface): The highlighted image displayed when hovered.
        rect (pygame.Rect): The rectangle defining the hover box's position and dimensions.

    Methods:
        update(screen: pygame.Surface, position: tuple[int, int]) -> None:
            Updates the hover box's appearance based on the mouse position,
            displaying either the default or highlighted image.

        check_for_input(position: tuple[int, int]) -> bool:
            Checks if the hover box was clicked and plays a click sound effect.
    """

    def __init__(
        self,
        position: tuple[float, float],
        image: pygame.Surface,
        image_highlited: pygame.Surface,
    ):
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.image = image
        self.image_highlighted = image_highlited
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen: pygame.Surface, position: tuple[int, int]):
        if position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom):
            screen.blit(self.image_highlighted, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def check_for_input(self, position: tuple[int, int]) -> bool:
        if position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom):
            play_on_empty(path="resources/button_click.mp3")
            return True
        return False
