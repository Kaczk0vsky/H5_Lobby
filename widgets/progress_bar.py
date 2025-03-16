import pygame
import time


class ProgressBar:
    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        background_color: pygame.Color = pygame.Color("gray"),
        progress_color: pygame.Color = pygame.Color("black"),
        text: str = "",
        text_color: pygame.Color = pygame.Color("green"),
        font_size: int = 20,
        image: pygame.Surface = None,
        max_wait_time: int = 10,
    ):
        self.x = position[0]
        self.y = position[1]
        self.length = dimensions[0]
        self.width = dimensions[1]
        self.rect = pygame.Rect(self.x, self.y, self.length, self.width)
        self.background_color = background_color
        self.progress_color = progress_color
        self.text = text
        self.image = image
        self.max_wait_time = max_wait_time
        if self.text:
            self.text_color = text_color
            self.font = pygame.font.Font("resources/ASansrounded.ttf", font_size)
            self.txt_surface = self.font.render(text, True, self.text_color)

    def draw(self, screen: pygame.Surface, elapsed_time: float) -> None:
        pygame.draw.rect(screen, self.background_color, self.rect)
        if self.text:
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.progress_color, self.rect, 2)

        progress_time = time.time() - elapsed_time
        fill_progress = progress_time / self.max_wait_time
        if fill_progress > 1:
            fill_progress = 1
            return True

        fill_width = int(self.length * fill_progress)
        fill_rect = pygame.Rect(self.x, self.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, self.progress_color, fill_rect)
        return False
