import pygame
import time


class ProgressBar:
    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        image_frame: pygame.Surface,
        image_bg: pygame.Surface,
        image_edge: pygame.Surface,
        max_wait_time: int = 10,
    ):
        self.x = position[0]
        self.y = position[1]
        self.length = dimensions[0]
        self.width = dimensions[1]
        self.image_frame = image_frame
        self.image_bg = image_bg
        self.image_edge = image_edge
        self.max_wait_time = max_wait_time
        self.rect = self.image_frame.get_rect(center=(self.x, self.y))
        self.rect_bg = self.image_bg.get_rect(center=(self.x, self.y))

    def draw(self, screen: pygame.Surface, elapsed_time: float) -> None:
        elapsed_time = time.time() - elapsed_time
        fill_progress = min(elapsed_time / self.max_wait_time, 1)
        fill_width = int(self.length * fill_progress)

        filled_bg = pygame.Surface((fill_width, self.width))
        filled_bg.blit(self.image_bg, (0, 0), (0, 0, fill_width, self.width))

        screen.blit(filled_bg, self.rect_bg)
        screen.blit(self.image_frame, self.rect)

        if fill_progress > 0 and fill_progress < 0.95:
            edge_rect = self.image_edge.get_rect(
                midleft=(
                    self.rect_bg.left + fill_width - self.image_edge.get_width() * 0.5,
                    self.rect_bg.centery,
                )
            )
            screen.blit(self.image_edge, edge_rect)

        if fill_progress == 1:
            return True
        return False
