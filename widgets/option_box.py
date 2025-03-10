import pygame


class OptionBox:
    """
    A class for creating an interactive dropdown option box.

    Attributes:
        color (pygame.Color): The default color of the option box.
        highlight_color (pygame.Color): The color when the option box is active or hovered.
        rect (pygame.Rect): The rectangle defining the position and size of the option box.
        font (pygame.font.Font): The font used for rendering the option text.
        option_list (list[str]): A list of selectable options.
        selected (int): The index of the currently selected option.
        draw_menu (bool): Determines whether the dropdown menu is visible.
        menu_active (bool): Indicates whether the main option box is active.
        active_option (int): The index of the currently highlighted option in the dropdown.

    Methods:
        draw(screen: pygame.Surface, x: float = None, y: float = None, width: int = None, height: int = None) -> None:
            Draws the option box on the given screen, including the dropdown menu if active.

        update(event_list: list) -> int | None:
            Updates the state of the option box based on mouse position and user input.
            Returns the index of the selected option if changed, otherwise None.
    """

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
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(position[0], position[1], dimensions[0], dimensions[1])
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(
        self,
        screen: pygame.Surface,
        x: float = None,
        y: float = None,
        width: int = None,
        hight: int = None,
    ) -> None:
        pygame.draw.rect(
            screen, self.highlight_color if self.menu_active else self.color, self.rect
        )
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        screen.blit(msg, msg.get_rect(center=self.rect.center))

        # resizing if given
        if x is not None:
            self.rect.x = x
        if y is not None:
            self.rect.y = y
        if width is not None:
            self.rect.width = width
        if hight is not None:
            self.rect.height = hight

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(
                    screen,
                    self.highlight_color if i == self.active_option else self.color,
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

    def update(self, event_list: list) -> None:
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option
        return None
