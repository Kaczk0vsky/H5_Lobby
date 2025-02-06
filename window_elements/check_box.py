import pygame

from src.helpers import play_on_empty


class CheckBox:
    def __init__(self, surface, x, y, w, h, checked=False):
        self.surface = surface
        self.x_pos = x
        self.y_pos = y
        self.base_color = pygame.Color("white")
        self.hovering_color = pygame.Color("gray")
        self.checked_color = pygame.Color("black")
        self.outer_rect = pygame.Rect(x, y, w, h)
        self.inner_rect = pygame.Rect(x + 2, y + 2, w - 4, h - 4)
        self.checked = checked
        self.is_active = False

    def draw(self):
        pygame.draw.rect(self.surface, self.checked_color, self.outer_rect)
        pygame.draw.rect(
            self.surface,
            self.base_color if self.is_active else self.hovering_color,
            self.inner_rect,
        )

    def update(self):
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

    def checkForInput(self, position):
        if position[0] in range(
            self.inner_rect.left, self.inner_rect.right
        ) and position[1] in range(self.inner_rect.top, self.inner_rect.bottom):
            self.checked = not self.checked
            self.is_active = True
            return True
        self.is_active = False
        return False
