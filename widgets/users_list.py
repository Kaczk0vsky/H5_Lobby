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
        scroll: pygame.Surface,
        scroll_bar: pygame.Surface,
        line: pygame.Surface,
        box: pygame.Surface,
        text: dict[str, list] = None,
    ):
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.color = color
        self.font = font
        self.title = title
        self.image = image
        self.image_box = image_box
        self.scroll = scroll
        self.scroll_bar = scroll_bar
        self.line = line
        self.box = box
        self.text = text

        self.title_surface = self.font.render(self.title, True, self.color)
        self.scroll_pos = 0
        self.scroll_dragging = False

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
        self.title_rect = self.title_surface.get_rect(
            center=(self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 10)
        )
        self.line_rect = pygame.Rect(
            self.x_pos - (self.rect.width / 2.65),
            self.y_pos - (self.rect.height / 2.75),
            self.line.get_width(),
            self.line.get_height(),
        )
        self.scroll_bar_rect = pygame.Rect(
            self.x_pos + (self.rect.width * 0.35),
            self.y_pos - (self.rect.height / 2.2),
            self.scroll_bar.get_width(),
            self.scroll_bar.get_height(),
        )
        self.scroll_rect = self.scroll.get_rect()
        self.scroll_rect.topleft = (
            self.x_pos + (self.rect.width * 0.3725),
            self.y_pos - (self.rect.height / 2.3),
        )

        if not self.text:
            self.text = ["essa", "essa2", "essa3"]

    def update(self, screen: pygame.Surface) -> None:
        screen.blit(self.image_bg, self.rect_bg)
        self.image_bg.fill((0, 0, 0, 220))
        screen.blit(self.image, self.rect)
        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.line, self.line_rect)
        screen.blit(self.scroll_bar, self.scroll_bar_rect)
        screen.blit(self.scroll, (self.scroll_rect.x, self.scroll_rect.y))

        # TODO: add dynamic users boxes
        # visible_items = 5
        # offset = int(
        #     (self.scroll_pos - (self.y_pos - (self.rect.height / 2.3)))
        #     / (self.scroll_bar.get_height() / len(self.text))
        # )

        # for index, value in enumerate(self.text[offset : offset + visible_items]):
        #     pygame.draw.rect(
        #         screen,
        #         (255, 255, 255),
        #         [
        #             self.x_pos - self.rect.w / 2.2,
        #             self.y_pos - self.rect.h / 3.3 + index * (self.rect.height / 6.2),
        #             self.rect.width - self.rect.width / 15,
        #             self.rect.height / 6,
        #         ],
        #         3,
        #     )

    def event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEWHEEL and self.rect_bg.collidepoint(
            (mouse_x, mouse_y)
        ):
            self.scroll_pos -= event.y * 10
            self.limit_scroll()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.scroll_rect.collidepoint(event.pos):
                self.scroll_dragging = True
            elif self.scroll_bar.get_rect(
                topleft=(
                    self.x_pos + (self.rect.width * 0.35),
                    self.y_pos - (self.rect.height / 2.2),
                )
            ).collidepoint(event.pos):
                self.scroll_pos = event.pos[1] - self.scroll.get_height() // 2
                self.limit_scroll()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.scroll_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.scroll_dragging:
            self.scroll_pos += event.rel[1]
            self.limit_scroll()

    def limit_scroll(self):
        min_y = self.y_pos - (self.rect.height / 2.3)
        max_y = (
            self.y_pos
            - (self.rect.height / 2.3)
            + (self.scroll_bar.get_height() * 0.96 - self.scroll.get_height())
        )
        self.scroll_pos = max(min_y, min(self.scroll_pos, max_y))
        self.scroll_rect.y = self.scroll_pos

    def get_data(self, text: list[str]):
        self.text = text
