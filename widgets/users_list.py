import pygame


class UsersList:
    def __init__(
        self,
        position: tuple[float, float],
        color: pygame.Color,
        font: pygame.font.Font,
        title: str,
        image: pygame.Surface,
        image_bg: pygame.Surface,
        image_box: pygame.Surface,
        text: dict[str, list] = None,
    ):
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.color = color
        self.font = font
        self.title = title
        self.image = image
        self.image_box = image_box
        self.text = text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.rect_bg = pygame.Rect(
            self.x_pos - (self.rect.width / 2.15),
            self.y_pos - (self.rect.height / 2.075),
            self.rect.width * 0.97,
            self.rect.height * 0.97,
        )
        self.image_bg = pygame.transform.scale(
            image_bg, (self.rect_bg.width, self.rect_bg.height)
        )
        # self.rect_player = self.image_box.get_rect(center=(self.x_pos, self.y_pos))
        # self.rect_player = pygame.draw.rect(screen, WHITE, [100, 100, 400, 300])
        self.title_surface = self.font.render(self.title, True, self.color)

        if not self.text:
            self.text = ["essa", "essa2", "essa3"]

    def update(self, screen: pygame.Surface) -> None:
        screen.blit(self.image_bg, self.rect_bg)
        self.image_bg.fill((0, 0, 0, 220))
        screen.blit(self.image, self.rect)
        title_rect = self.title_surface.get_rect(
            center=(self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 10)
        )
        screen.blit(self.title_surface, title_rect)
        # screen.blit(self.image_box, self.rect_player)

        for index, value in enumerate(self.text):
            pygame.draw.rect(
                screen,
                (255, 255, 255),  # white
                [
                    self.x_pos - self.rect.w / 2.2,
                    self.y_pos - self.rect.h / 3.3 + index * (self.rect.height / 6.2),
                    self.rect.width - self.rect.width / 15,
                    self.rect.height / 6,
                ],
                3,
            )

    def get_data(self, text: list[str]):
        self.text = text
