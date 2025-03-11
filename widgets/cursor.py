import pygame
import os


class Cursor:
    """Manages custom mouse cursors for different interactions in a Pygame application.

    This class loads and sets different cursor images based on user interactions:
    - Default cursor.
    - Clicked cursor (when the left mouse button is pressed).
    - Cursed cursor (when the right mouse button is pressed).
    """

    def __init__(self):
        pygame.init()
        self.CURSOR_IMAGE = pygame.transform.scale(
            pygame.image.load(
                os.path.join(os.getcwd(), "resources/cursors/cursor1.png")
            ),
            (32, 32),
        )
        self.CURSOR_IMAGE_CLICKED = pygame.transform.scale(
            pygame.image.load(
                os.path.join(os.getcwd(), "resources/cursors/cursor2.png")
            ),
            (32, 32),
        )
        self.CURSOR_IMAGE_CURSED = pygame.transform.scale(
            pygame.image.load(
                os.path.join(os.getcwd(), "resources/cursors/cursor3.png")
            ),
            (60, 60),
        )
        self.cursor = pygame.cursors.Cursor((8, 8), self.CURSOR_IMAGE)
        self.cursor_clicked = pygame.cursors.Cursor((8, 8), self.CURSOR_IMAGE_CLICKED)
        self.cursor_cursed = pygame.cursors.Cursor((30, 30), self.CURSOR_IMAGE_CURSED)

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            pygame.mouse.set_cursor(self.cursor_clicked)
        elif pygame.mouse.get_pressed()[2]:
            pygame.mouse.set_cursor(self.cursor_cursed)
        else:
            pygame.mouse.set_cursor(self.cursor)
