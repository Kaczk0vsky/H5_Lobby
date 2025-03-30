import pygame


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

    _active_option = -1
    _draw_menu = False
    _menu_active = False

    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        color: pygame.Color,
        highlight_color: pygame.Color,
        font: pygame.font.Font,
        option_list: list,
        selected: int = 0,
    ):
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.w = dimensions[0]
        self.h = dimensions[1]
        self.color = color
        self.highlight_color = highlight_color
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.rect = pygame.Rect(self.x_pos, self.y_pos, self.w, self.h)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen, self.highlight_color if self._menu_active else self.color, self.rect
        )
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        screen.blit(msg, msg.get_rect(center=self.rect.center))

        if self._draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(
                    screen,
                    self.highlight_color if i == self._active_option else self.color,
                    rect,
                )
                msg = self.font.render(text, 1, (0, 0, 0))
                screen.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
                self.rect.x,
                self.rect.y + self.rect.height,
                self.rect.width,
                self.rect.height * len(self.option_list),
            )
            pygame.draw.rect(screen, (0, 0, 0), outer_rect, 2)

    def update(self, event_list: list) -> int:
        mpos = pygame.mouse.get_pos()
        self._menu_active = self.rect.collidepoint(mpos)

        self._active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self._active_option = i
                break

        if not self._menu_active and self._active_option == -1:
            self._draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._menu_active:
                    self._draw_menu = not self._draw_menu
                elif self._draw_menu and self._active_option >= 0:
                    self.selected = self._active_option
                    self._draw_menu = False
                    return self._active_option
        return -1
