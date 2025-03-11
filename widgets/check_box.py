import pygame


class CheckBox:
    """
    A class for creating a CheckBox.

    Attributes:
        surface (pygame.Surface): The surface on which the checkbox will be drawn.
        position (tuple[int, int]): The (x, y) position of the checkbox.
        dimensions (tuple[int, int]): The width and height of the checkbox.
        state (bool): The initial state of the checkbox (checked or unchecked).

    Methods:
        draw():
            Draws an empty checkbox on the selected surface.

        update():
            Changes the state if clicked. Draws an 'X' with black lines inside
            or an empty white background.

        check_for_input():
            Checks if a mouse click was detected inside the checkbox borders.
    """

    def __init__(
        self,
        surface: pygame.Surface,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        checked: bool = False,
    ):
        self.surface = surface
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.base_color = pygame.Color("white")
        self.hovering_color = pygame.Color("gray")
        self.checked_color = pygame.Color("black")
        self.outer_rect = pygame.Rect(
            position[0], position[1], dimensions[0], dimensions[1]
        )
        self.inner_rect = pygame.Rect(
            position[0] + 2, position[1] + 2, dimensions[0] - 4, dimensions[1] - 4
        )
        self.checked = checked
        self.is_active = False

    def draw(self) -> None:
        pygame.draw.rect(self.surface, self.checked_color, self.outer_rect)
        pygame.draw.rect(
            self.surface,
            self.base_color if self.is_active else self.hovering_color,
            self.inner_rect,
        )

    def update(self) -> None:
        self.draw()
        if self.checked:
            pygame.draw.line(
                self.surface,
                self.checked_color,
                (self.inner_rect.x, self.inner_rect.y),
                (
                    self.inner_rect.x + self.inner_rect.w,
                    self.inner_rect.y + self.inner_rect.h,
                ),
                3,
            )
            pygame.draw.line(
                self.surface,
                self.checked_color,
                (self.inner_rect.x + self.inner_rect.w, self.inner_rect.y),
                (self.inner_rect.x, self.inner_rect.y + self.inner_rect.h),
                3,
            )
        else:
            pygame.draw.rect(
                self.surface,
                self.base_color if self.is_active else self.hovering_color,
                self.inner_rect,
            )

    def check_for_input(self, position: tuple[int, int]) -> bool:
        if position[0] in range(
            self.inner_rect.left, self.inner_rect.right
        ) and position[1] in range(self.inner_rect.top, self.inner_rect.bottom):
            self.checked = not self.checked
            self.is_active = True
            return True
        self.is_active = False
        return False
