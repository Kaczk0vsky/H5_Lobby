import pygame
import time


class ProgressBar:
    """
    A graphical progress bar for tracking elapsed time in a Pygame application.

    This class visually represents the progress of a timer using images for
    the frame, background, and edge, updating the display based on elapsed time.

    Attributes:
        x_pos (float): The x-coordinate of the progress bar's center.
        y_pos (float): The y-coordinate of the progress bar's center.
        w (int): The total length of the progress bar.
        h (int): The height of the progress bar.
        image_frame (pygame.Surface): The image representing the progress bar's frame.
        image_bg (pygame.Surface): The image representing the progress bar's background.
        image_edge (pygame.Surface): The image representing the moving edge of the progress bar.
        max_wait_time (int): The maximum duration (in seconds) before the progress bar is fully filled.
        rect (pygame.Rect): The rectangle representing the position of the frame image.
        rect_bg (pygame.Rect): The rectangle representing the position of the background image.

    Methods:
        draw(screen: pygame.Surface, elapsed_time: float) -> bool:
            Updates and renders the progress bar on the given screen surface based on the elapsed time.
            Returns True when the progress bar is fully filled, otherwise returns False.
    """

    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        image_frame: pygame.Surface,
        image_bg: pygame.Surface,
        image_edge: pygame.Surface,
        max_wait_time: int = 10,
    ):
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.w = dimensions[0]
        self.h = dimensions[1]
        self.image_edge = pygame.transform.scale(image_edge, (self.w / 10, self.h * 1.5))
        self.max_wait_time = max_wait_time
        self.image_frame = pygame.transform.scale(image_frame, (self.w, self.h))
        self.rect = self.image_frame.get_rect(center=(self.x_pos, self.y_pos))
        self.image_bg = pygame.transform.scale(image_bg, (self.w * 0.9, self.h * 0.8))
        self.rect_bg = self.image_bg.get_rect(center=(self.x_pos + self.w * 0.02, self.y_pos + self.h * 0.175))

    def draw(self, screen: pygame.Surface, elapsed_time: float) -> bool:
        elapsed_time = time.time() - elapsed_time
        fill_progress = min(elapsed_time / self.max_wait_time, 1)
        fill_width = int((self.w * 0.875) * fill_progress)

        filled_bg = pygame.Surface((fill_width, self.h / 2))
        filled_bg.blit(self.image_bg, (0, 0), (0, 0, fill_width, self.h))

        screen.blit(filled_bg, self.rect_bg)
        screen.blit(self.image_frame, self.rect)

        if fill_progress > 0 and fill_progress < 0.95:
            edge_rect = self.image_edge.get_rect(
                midleft=(
                    self.rect_bg.left + fill_width - self.image_edge.get_width() * 0.5,
                    self.rect_bg.centery * 0.98,
                )
            )
            screen.blit(self.image_edge, edge_rect)

        if fill_progress == 1:
            return True
        return False
