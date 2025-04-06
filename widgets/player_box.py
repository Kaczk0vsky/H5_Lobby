import pygame


class PlayerBox:
    """
    A class representing a single player entry in a user list, displaying nickname, ranking points, and status.

    Attributes:
        position (tuple[float, float]): The x and y coordinates of the top-left corner of the box.
        dimensions (tuple[int, int]): The width and height of the player box.
        color (pygame.Color): The color used for rendering the text.
        red (str): Hex color code used for offline or inactive status.
        green (str): Hex color code used for online or active status.
        font (pygame.font.Font): The main font used for the nickname.
        font_small (pygame.font.Font): A smaller font used for additional player info.
        nickname (str): The player's nickname.
        ranking_points (int): The player's ranking points.
        state (str): The player's current status (e.g., "online", "offline").
        green_states (list[str]): List of states that are considered "green" (active).
        rect (pygame.Rect): The rectangle representing the box's position and size.
        image_line (pygame.Surface): A line image rendered at the bottom of the box.
        image_box (pygame.Surface): A graphic/icon displayed next to the player’s name.

        text_surface_nickname (pygame.Surface): Rendered text surface for the nickname.
        text_surface_points (pygame.Surface): Rendered text surface for ranking points.
        text_surface_status_title (pygame.Surface): Rendered label for status.
        text_surface_status (pygame.Surface): Rendered text surface showing the player’s current status.

    Methods:
        update(screen: pygame.Surface) -> None:
            Draws the player box on the screen, including the nickname, ranking points, status,
            player icon, and decorative line.
    """

    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        color: pygame.Color,
        font: pygame.font.Font,
        nickname: str,
        ranking_points: int,
        state: str,
        image_line: pygame.Surface,
        image_box: pygame.Surface,
    ):
        self.w = dimensions[0]
        self.h = dimensions[1]
        self.color = color
        self.red = "#db1102"
        self.green = "#02ba09"
        self.font = font
        self.font_small = pygame.font.Font(
            "resources/Quivira.otf", int(self.font.get_height() * 0.6)
        )
        self.nickname = nickname
        self.ranking_points = ranking_points
        self.state = state
        self.green_states = ["Online", "In queue"]
        self.rect = pygame.Rect(position, dimensions)
        self.image_line = pygame.transform.scale(
            image_line, (self.w, image_line.get_height() * 0.4)
        )
        self.image_box = pygame.transform.scale(
            image_box, (image_box.get_width() * 1.25, image_box.get_height() * 1.25)
        )

        self.text_surface_nickname = self.font.render(self.nickname, True, self.color)
        self.text_surface_points = self.font_small.render(
            f"Ranking points: {self.ranking_points}", True, self.color
        )
        self.text_surface_status_title = self.font_small.render(
            "Status: ", True, self.color
        )
        self.text_surface_status = self.font_small.render(
            self.state,
            True,
            self.green if str(self.state) in self.green_states else self.red,
        )

    def update_surfaces(self):
        self.text_surface_nickname = self.font.render(self.nickname, True, self.color)
        self.text_surface_points = self.font_small.render(
            f"Ranking points: {self.ranking_points}", True, self.color
        )
        self.text_surface_status_title = self.font_small.render(
            "Status: ", True, self.color
        )
        self.text_surface_status = self.font_small.render(
            self.state,
            True,
            self.green if str(self.state) in self.green_states else self.red,
        )

    def update(self, screen: pygame.Surface) -> None:
        text_x = self.rect.x + self.w * 0.075
        text_y = self.rect.y + self.h * 0.1

        screen.blit(self.text_surface_nickname, (text_x + self.w * 0.15, text_y))
        screen.blit(self.text_surface_points, (text_x, text_y + self.h * 0.4))
        screen.blit(
            self.text_surface_status_title,
            (text_x, text_y + self.h * 0.625),
        )
        screen.blit(
            self.text_surface_status,
            (
                text_x + self.text_surface_status_title.get_width(),
                text_y + self.h * 0.625,
            ),
        )

        if self.image_box:
            image_x = self.rect.x + self.w * 0.075
            image_y = self.rect.y + self.h * 0.02
            screen.blit(self.image_box, (image_x, image_y))

        if self.image_line:
            image_x = self.rect.x + self.w - self.image_line.get_width()
            image_y = self.rect.y + self.h
            screen.blit(self.image_line, (image_x, image_y))
