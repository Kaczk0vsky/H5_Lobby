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
            pygame.image.load(os.path.join(os.getcwd(), "resources/cursors/cursor1.png")),
            (32, 32),
        )
        self.CURSOR_IMAGE_CLICKED = pygame.transform.scale(
            pygame.image.load(os.path.join(os.getcwd(), "resources/cursors/cursor2.png")),
            (32, 32),
        )
        self.CURSOR_IMAGE_CURSED = pygame.transform.scale(
            pygame.image.load(os.path.join(os.getcwd(), "resources/cursors/cursor3.png")),
            (60, 60),
        )
        self.cursor = pygame.Cursor((8, 8), self.CURSOR_IMAGE)
        self.cursor_clicked = pygame.Cursor((8, 8), self.CURSOR_IMAGE_CLICKED)
        self.cursor_cursed = pygame.Cursor((30, 30), self.CURSOR_IMAGE_CURSED)

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            if self.cursor_clicked:
                self.set_cursor(self.cursor_clicked)
        elif pygame.mouse.get_pressed()[2]:
            if self.cursor_cursed:
                self.set_cursor(self.cursor_cursed)
        else:
            if self.cursor:
                self.set_cursor(self.cursor)

    @staticmethod
    def set_cursor(cursor: pygame.Cursor):
        try:
            pygame.mouse.set_cursor(cursor)
        except pygame.error:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
