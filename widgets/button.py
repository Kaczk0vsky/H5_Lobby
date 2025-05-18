import pygame

from src.helpers import play_on_empty, render_small_caps


class Button:
    """
    A class for creating an interactive button with different states.

    Attributes:
        position (tuple[float, float]): The x and y coordinates of the button's position.
        image (pygame.Surface): The default image of the button.
        image_highlighted (pygame.Surface): The highlighted version of the button image.
        font (pygame.font.Font): The font used for the button's text.
        base_color (str): The default text color.
        hovering_color (str): The text color when hovered over.
        text_input (str): The text displayed inside the button (default: "").
        image_inactive (pygame.Surface, optional): The inactive version of the button image.
        inactive_color (str, optional): The text color when the button is inactive.

    Methods:
        update(screen: pygame.Surface, position: tuple[int, int]) -> None:
            Updates the button's appearance based on the mouse position and draws it on the screen.
            Displays the highlighted, default, or inactive image accordingly.

        check_for_input(position: tuple[int, int]) -> bool:
            Checks if the button is clicked and plays a click sound if active.

        change_color(position: tuple[int, int]) -> None:
            Changes the button's text color based on hover state and activation status.

        handle_button(screen: pygame.Surface, position: tuple[int, int]) -> None:
            Manages both color changes and rendering of the button.

        set_active(is_active: bool = True) -> None:
            Enables or disables the button, changing its appearance accordingly.
    """

    def __init__(
        self,
        position: tuple[float, float],
        image: pygame.Surface,
        image_highlited: pygame.Surface,
        font_size: int,
        base_color: str,
        hovering_color: str,
        text_input: str = "",
        image_inactive: pygame.Surface = None,
        inactive_color: str = None,
    ):
        self.image = image
        self.image_highlighted = image_highlited
        self.original_image = image
        self.original_image_highlighted = image_highlited
        self.x_pos = position[0]
        self.y_pos = position[1]
        self.original_x_pos = position[0]
        self.original_y_pos = position[1]
        self.font_size = font_size
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.inactive_color = base_color
        self.image_inactive = image_inactive or image
        self.original_image_inactive = image_inactive or image

        if inactive_color:
            self.inactive_color = inactive_color
        if image_inactive:
            self.image_inactive = image_inactive
        if self.text_input:
            self.text = render_small_caps(self.text_input, self.font_size, self.base_color)
            self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        if self.image is None:
            self.image = self.text

        self.active = True

    def __update(self, screen: pygame.Surface, position: tuple[int, int]) -> None:
        if self.active:
            if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
                if self.image_highlighted is not None:
                    screen.blit(self.image_highlighted, self.rect)
            else:
                if self.image is not None:
                    screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image_inactive, self.rect)
        if self.text_input:
            screen.blit(self.text, self.text_rect)

    def __change_color(self, position: tuple[int, int]) -> None:
        if self.active:
            if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
                self.text = render_small_caps(self.text_input, self.font_size, self.hovering_color)
            else:
                self.text = render_small_caps(self.text_input, self.font_size, self.base_color)
        else:
            self.text = render_small_caps(self.text_input, self.font_size, self.inactive_color)

    def __set_font_size(self, new_font_size: int):
        self.font_size = new_font_size

    def __calculate_new_dimensions(self, scale: tuple[float, float]):
        self.x_pos = self.original_x_pos * scale[0]
        self.y_pos = self.original_y_pos * scale[1]

        new_width = int(self.original_image.get_width() * scale[0])
        new_height = int(self.original_image.get_height() * scale[1])

        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))
        self.image_highlighted = pygame.transform.scale(self.original_image_highlighted, (new_width, new_height))
        self.image_inactive = pygame.transform.scale(self.original_image_inactive, (new_width, new_height))

        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        if self.text_input:
            self.text = render_small_caps(self.text_input, self.font_size, self.base_color)
            self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def handle_button(self, screen: pygame.Surface, position: tuple[int, int]) -> None:
        if self.text_input:
            self.__change_color(position=position)
        self.__update(screen=screen, position=position)

    def check_for_input(self, position: tuple[int, int]) -> bool:
        if self.active:
            if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
                play_on_empty(path="resources/button_click.mp3")
                return True
            return False

    def set_active(self, is_active: bool = True) -> None:
        self.active = is_active

    def rescale(self, new_font_size: int, scale: tuple[float, float]):
        self.__set_font_size(new_font_size)
        self.__calculate_new_dimensions(scale)
