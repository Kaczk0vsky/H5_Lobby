import pygame

from src.helpers import play_on_empty


class HoverBox:
    def __init__(
        self,
        image: pygame.Surface,
        image_highlited: pygame.Surface,
        pos: tuple[float, float],
        dimensions: tuple[int, int],
    ):
        self.image = image
        self.image_highlighted = image_highlited
        self.pos = pos
        self.dims = dimensions
        self.active = False
        self.rect = self.image.get_rect(center=(self.pos[0], self.pos[1]))

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
            self.channel_index = play_on_empty("resources/button_click.mp3")
            self.active = True
            return True
        return False
