import pygame


class TextInput:
    def __init__(
        self,
        x,
        y,
        w,
        h,
        text="",
        color_inactive=pygame.Color("black"),
        color_active=pygame.Color("gray"),
        fill_inactive=pygame.Color("gray"),
        fill_active=pygame.Color("white"),
        font_size=20,
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color_inactive
        self.color_inactive = color_inactive
        self.color_active = color_active
        self.fill_inactive = fill_inactive
        self.fill_active = fill_active
        self.hidden_text = text
        self.text = text
        self.FONT = pygame.font.Font("resources/ASansrounded.ttf", font_size)
        self.txt_surface = self.FONT.render(text, True, pygame.Color("black"))
        self.active = False

    def event(self, event, hide_text=False):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.FONT.render(
                    self.text, True, pygame.Color("black")
                )

    def button_pressed(self, button_pressed=False):
        if button_pressed:
            return self.text

    def update(self):
        # resizing, dont know if needed
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Fill the rect with the fill color based on active status
        fill_color = self.fill_active if self.active else self.fill_inactive
        pygame.draw.rect(screen, fill_color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
