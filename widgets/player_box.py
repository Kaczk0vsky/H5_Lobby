import pygame


class PlayerBox:
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
        self.green_states = ["online", "in queue"]
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

    def update(self, screen: pygame.Surface):
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
