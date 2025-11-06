import pygame

from src.helpers import render_small_caps, play_on_empty_channel


class OptionBox:
    """
    A class for creating an interactive dropdown option box in Pygame.

    Attributes:
        position (tuple[float, float]): The x and y coordinates of the option box.
        dimensions (tuple[int, int]): The width and height of the option box.
        color (pygame.Color): The default background color of the option box.
        highlight_color (pygame.Color): The color used when the box is active or hovered.
        font (pygame.font.Font): The font used for rendering the option text.
        option_list (list[str]): A list of available selectable options.
        selected (int): The index of the currently selected option.
        rect (pygame.Rect): The rectangle defining the position and size of the option box.
        _active_option (int): The index of the currently highlighted option in the dropdown.
        _draw_menu (bool): Determines whether the dropdown menu is visible.
        _menu_active (bool): Indicates whether the main option box is active.

    Methods:
        draw(screen: pygame.Surface) -> None:
            Draws the option box on the given screen, including the dropdown menu if active.

        update(event_list: list) -> int:
            Handles mouse events, updates the selection state, and toggles menu visibility.
            Returns the index of the selected option if changed, otherwise -1.
    """

    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        arrow_left: pygame.Surface,
        arrow_left_highlighted: pygame.Surface,
        arrow_right: pygame.Surface,
        arrow_right_highlighted: pygame.Surface,
        color: pygame.Color,
        highlight_color: pygame.Color,
        font_size: int,
        option_list: list,
        selected: int = 0,
    ):
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.w = dimensions[0]
        self.h = dimensions[1]
        self.arrow_left = arrow_left
        self.arrow_left_highlighted = arrow_left_highlighted
        self.arrow_right = arrow_right
        self.arrow_right_highlighted = arrow_right_highlighted
        self.color = color
        self.highlight_color = highlight_color
        self.font_size = font_size
        self.option_list = option_list
        self.selected = self.option_list.index(selected)

        self.text = render_small_caps(self.option_list[self.selected], self.font_size, self.color)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        self._update_arrow_rects()

    def _update_arrow_rects(self):
        center_y = self.text_rect.centery

        self.arrow_left_rect = self.arrow_left.get_rect()
        self.arrow_left_rect.midright = (self.text_rect.left - self.text_rect.width * 0.1, center_y)

        self.arrow_right_rect = self.arrow_right.get_rect()
        self.arrow_right_rect.midleft = (self.text_rect.right + self.text_rect.width * 0.1, center_y)

    def update(self, screen: pygame.Surface, position: tuple[int, int]) -> int:
        self.text = render_small_caps(self.option_list[self.selected], self.font_size, self.color)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

        self._update_arrow_rects()
        screen.blit(self.text, self.text_rect)

        if self.arrow_left_rect.collidepoint(position):
            screen.blit(self.arrow_left_highlighted, self.arrow_left_rect)
        else:
            screen.blit(self.arrow_left, self.arrow_left_rect)

        if self.arrow_right_rect.collidepoint(position):
            screen.blit(self.arrow_right_highlighted, self.arrow_right_rect)
        else:
            screen.blit(self.arrow_right, self.arrow_right_rect)

    def check_for_input(self, position: tuple[int, int]) -> bool:
        if self.arrow_left_rect.collidepoint(position):
            play_on_empty_channel(path="resources/button_click.mp3")
            self.selected -= 1
            if self.selected == -1:
                self.selected = len(self.option_list) - 1
            return True

        if self.arrow_right_rect.collidepoint(position):
            play_on_empty_channel(path="resources/button_click.mp3")
            self.selected += 1
            if self.selected == len(self.option_list):
                self.selected = 0
            return True

        return False

    def get_selected_option(self):
        return self.option_list[self.selected]
