import pygame

from widgets.player_box import PlayerBox
from src.helpers import render_small_caps


class UsersList:
    """
    A class for displaying a scrollable list of player profiles.

    Attributes:
        position (tuple[float, float]): The x and y coordinates of the center position of the list.
        color (pygame.Color): The color used for rendering text and player boxes.
        font (pygame.font.Font): The font used for rendering text.
        title (str): The title displayed at the top of the list.
        image (pygame.Surface): The background image of the entire list container.
        image_bg (pygame.Surface): The background image of the inner box.
        image_box (pygame.Surface): The image used for player box backgrounds.
        scroll (pygame.Surface): The scroll handle image.
        scroll_bar (pygame.Surface): The scroll bar background image.
        line (pygame.Surface): A decorative line under the title.
        box (pygame.Surface): A surface used to create the individual player boxes.
        text (dict[str, list], optional): Dictionary containing player information in the format {nickname: [ranking_points, state]}.

    Methods:
        update(screen: pygame.Surface) -> None:
            Renders the entire user list, including the background, title, line, scroll bar, and player boxes.
            Handles scrolling animation.

        event(event) -> None:
            Handles mouse wheel and button events for scrolling and dragging the scroll handle.

        limit_scroll() -> None:
            Clamps the scroll position within the scroll bar's range.

        limit_scroll_target() -> None:
            Clamps the target scroll position to prevent overscrolling when using the mouse wheel.

        get_players_list(text: dict[str, list] = {}) -> None:
            Initializes and generates the list of player boxes based on the provided text dictionary.
    """

    def __init__(
        self,
        position: tuple[float, float],
        color: pygame.Color,
        hovering_color: pygame.Color,
        font_size: int,
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
        self.hovering_color = hovering_color
        self.font_size = font_size
        self.title = title
        self.image = image
        self.image_box = image_box
        self.scroll = scroll
        self.scroll_bar = scroll_bar
        self.line = line
        self.box = box
        self.text = text

        self.scroll_dragging = False
        self.player_list = []

        self.title_surface = render_small_caps(self.title, self.font_size, self.color)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.rect_bg = pygame.Rect(
            self.x_pos - (self.rect.width / 2.15),
            self.y_pos - (self.rect.height / 2.075),
            self.rect.width * 0.97,
            self.rect.height * 0.95,
        )
        self.image_bg = pygame.transform.scale(image_bg, (self.rect_bg.width, self.rect_bg.height))
        self.title_rect = self.title_surface.get_rect(center=(self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 10))
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
        self.scroll_pos = self.scroll_bar_rect.top
        self.target_scroll_pos = self.scroll_pos
        self.scroll_rect = self.scroll.get_rect()
        self.scroll_rect.topleft = (
            self.x_pos + (self.rect.width * 0.3725),
            self.scroll_pos,
        )
        self.scroll_area_rect = pygame.Rect(
            self.rect_bg.left,
            self.line_rect.bottom,
            self.rect_bg.width,
            self.rect_bg.bottom - self.line_rect.bottom,
        )

    def update(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        screen.blit(self.image_bg, self.rect_bg)
        self.image_bg.fill((0, 0, 0, 220))
        screen.blit(self.title_surface, self.title_rect)
        screen.blit(self.line, self.line_rect)

        player_height = self.rect.height / 10
        padding_bottom = player_height * 0.2825

        max_scroll = max(
            0,
            len(self.player_list) * player_height - self.rect_bg.height + padding_bottom,
        )
        scroll_range = self.scroll_bar_rect.height - self.scroll.get_height()

        if not self.scroll_dragging:
            lerp_speed = 0.15  # speed of scroll bar
            self.scroll_pos += (self.target_scroll_pos - self.scroll_pos) * lerp_speed
        else:
            self.target_scroll_pos = self.scroll_pos
        self.scroll_rect.y = self.scroll_pos
        scroll_percent = (self.scroll_pos - self.scroll_bar_rect.top) / scroll_range if scroll_range > 0 else 0
        scroll_offset = scroll_percent * max_scroll

        old_clip = screen.get_clip()
        screen.set_clip(self.scroll_area_rect)

        for player, base_y in self.player_list:
            player_y = base_y - scroll_offset
            player.rect.y = player_y
            player.update(screen, mouse_pos)

        screen.set_clip(old_clip)

        screen.blit(self.image, self.rect)
        screen.blit(self.scroll_bar, self.scroll_bar_rect)
        screen.blit(self.scroll, (self.scroll_rect.x, self.scroll_rect.y))

    def event(self, event) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for player, base_y in self.player_list:
            player.event(event, (mouse_x, mouse_y))

        if event.type == pygame.MOUSEWHEEL and self.rect_bg.collidepoint((mouse_x, mouse_y)):
            self.target_scroll_pos -= event.y * len(self.text) * 3
            self.limit_scroll_target()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.scroll_rect.collidepoint(event.pos):
                self.scroll_dragging = True
            elif self.scroll_bar.get_rect(
                topleft=(
                    self.x_pos + (self.rect.width * 0.35),
                    self.y_pos - (self.rect.height / 2.2),
                )
            ).collidepoint(event.pos):
                self.target_scroll_pos = event.pos[1] - self.scroll.get_height() // 2
                self.limit_scroll_target()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.scroll_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.scroll_dragging:
            self.scroll_pos += event.rel[1]
            self.limit_scroll()

    def limit_scroll(self) -> None:
        min_y = self.scroll_bar_rect.top
        max_y = self.scroll_bar_rect.bottom - self.scroll.get_height()
        self.scroll_pos = max(min_y, min(self.scroll_pos, max_y))
        self.scroll_rect.y = self.scroll_pos

    def limit_scroll_target(self) -> None:
        min_y = self.scroll_bar_rect.top
        max_y = self.scroll_bar_rect.bottom - self.scroll.get_height()
        self.target_scroll_pos = max(min_y, min(self.target_scroll_pos, max_y))

    def get_players_list(self, text: dict[str, list] = {}) -> None:
        self.text = text
        temp_list = []
        if self.player_list:
            existing_nicknames = {player.nickname for player, _ in self.player_list}
            for index, (key, value) in enumerate(text.items()):
                y_offset = index * (self.rect.height / 10)
                base_y = self.y_pos - self.rect.h / 2.8 + y_offset
                if key in existing_nicknames:
                    for player, y in self.player_list:
                        if player.nickname == key:
                            player.ranking_points = value[0]
                            player.state = value[1]
                            player.update_surfaces()
                            temp_list.append((player, base_y))
                            break
                else:
                    player = PlayerBox(
                        position=(self.x_pos - self.rect.w / 2.2, base_y),
                        dimensions=(
                            self.rect.width - self.rect.width / 15,
                            self.rect.height / 10,
                        ),
                        color=self.color,
                        hovering_color=self.hovering_color,
                        font_size=self.font_size,
                        nickname=key,
                        ranking_points=value[0],
                        state=value[1],
                        state_info="Ranked" if value[2] else "Unranked",
                        image_line=self.line,
                        image_box=self.box,
                    )
                    temp_list.append((player, base_y))
        else:
            for index, (key, value) in enumerate(self.text.items()):
                y_offset = index * (self.rect.height / 10)
                base_y = self.y_pos - self.rect.h / 2.8 + y_offset

                player = PlayerBox(
                    position=(self.x_pos - self.rect.w / 2.2, base_y),
                    dimensions=(
                        self.rect.width - self.rect.width / 15,
                        self.rect.height / 10,
                    ),
                    color=self.color,
                    hovering_color=self.hovering_color,
                    font_size=self.font_size,
                    nickname=key,
                    ranking_points=value[0],
                    state=value[1],
                    state_info="Ranked" if value[2] else "Unranked",
                    image_line=self.line,
                    image_box=self.box,
                )
                temp_list.append((player, base_y))
        self.player_list = temp_list
