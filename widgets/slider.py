import pygame

from src.helpers import render_small_caps


class Slider:
    __dragging = False

    def __init__(
        self,
        position: tuple[float, float],
        scroll: pygame.Surface,
        scroll_marker: pygame.Surface,
        color: pygame.Color,
        font_size: int,
        selected_value: str,
    ):
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.scroll = scroll
        self.scroll_marker = scroll_marker
        self.color = color
        self.font_size = font_size
        self.selected_value = int(selected_value)

        self.scroll_rect = self.scroll.get_rect()
        self.scroll_marker_rect = self.scroll_marker.get_rect()

        effective_left = self.x_pos + self.scroll.get_width() * 0.1
        effective_right = self.x_pos + self.scroll.get_width() * 0.9
        effective_width = effective_right - effective_left
        marker_x = effective_left + (self.selected_value / 100) * effective_width

        self.scroll_rect.topleft = (self.x_pos, self.y_pos)
        effective_left = self.scroll_rect.left + self.scroll_rect.width * 0.1
        self.scroll_marker_rect.center = (marker_x, self.scroll_rect.centery)

    def update_slider(self, position: tuple[int, int]) -> int:
        mouse_x, mouse_y = position
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.scroll_marker_rect.collidepoint(mouse_x, mouse_y):
            if mouse_pressed:
                self.__dragging = True
        if not mouse_pressed:
            self.__dragging = False

        if self.__dragging:
            new_x = max(self.scroll_rect.left + self.scroll_rect.width * 0.1, min(mouse_x, self.scroll_rect.right - self.scroll_rect.width * 0.1))
            self.scroll_marker_rect.centerx = new_x
            self.scroll_marker_rect.centery = self.scroll_rect.centery

    def draw(self, screen: pygame.Surface) -> int:
        self.scroll_rect.topleft = (self.x_pos, self.y_pos)
        screen.blit(self.scroll, self.scroll_rect)
        screen.blit(self.scroll_marker, self.scroll_marker_rect)

        effective_left = self.scroll_rect.left + self.scroll_rect.width * 0.1
        effective_right = self.scroll_rect.right - self.scroll_rect.width * 0.1
        effective_width = effective_right - effective_left

        relative_pos = self.scroll_marker_rect.centerx - effective_left
        self.selected_value = int((relative_pos / effective_width) * 100)

        text_surface = render_small_caps(str(self.selected_value), self.font_size, self.color)
        text_rect = text_surface.get_rect()
        text_rect.midleft = (self.scroll_rect.right + self.scroll_rect.width * 0.025, self.scroll_rect.centery)
        screen.blit(text_surface, text_rect)

    def get_slider_value(self):
        return self.selected_value
