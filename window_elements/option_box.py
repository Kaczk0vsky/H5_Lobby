import pygame


class OptionBox:
    def __init__(
        self, x, y, w, h, color, highlight_color, font, option_list, selected=0
    ):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(
        self,
        surf,
        x=None,
        y=None,
        width=None,
        hight=None,
    ):
        pygame.draw.rect(
            surf, self.highlight_color if self.menu_active else self.color, self.rect
        )
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

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
                    surf,
                    self.highlight_color if i == self.active_option else self.color,
                    rect,
                )
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
                self.rect.x,
                self.rect.y + self.rect.height,
                self.rect.width,
                self.rect.height * len(self.option_list),
            )
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update(self, event_list):
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
