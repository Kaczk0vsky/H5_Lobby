import pygame


class TextInput:
    _id = 0
    _instances = []
    _key_pressed = False

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        text: str = "",
        color_inactive: pygame.Color = pygame.Color("black"),
        color_active: pygame.Color = pygame.Color("gray"),
        fill_inactive: pygame.Color = pygame.Color("gray"),
        fill_active: pygame.Color = pygame.Color("white"),
        font_size: int = 20,
    ):
        self.id = TextInput._id
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

        TextInput._id += 1
        TextInput._instances.append(self)

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
                    if hide_text:
                        self.hidden_text = self.hidden_text[:-1]
                elif event.key == pygame.K_TAB:
                    if not self._key_pressed:
                        self.jump_to_next_input()
                elif event.key == pygame.K_RETURN:
                    print("Enter key pressed!")
                else:
                    if hide_text:
                        self.text += "*"
                        self.hidden_text += event.unicode
                    else:
                        self.text += event.unicode
                self.txt_surface = self.FONT.render(
                    self.text, True, pygame.Color("black")
                )
        if event.type == pygame.KEYUP:
            if self.active:
                for instance in TextInput._instances:
                    instance._key_pressed = False

    def button_pressed(self, button_pressed=False):
        if button_pressed:
            if len(self.text) == len(self.hidden_text):
                return self.hidden_text
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

    def jump_to_next_input(self):
        self.active = False
        self._key_pressed = False
        next_id = self.id + 1

        next_instance = None
        for instance in TextInput._instances:
            if instance.id == next_id:
                next_instance = instance
                break
        if not next_instance:
            next_instance = TextInput._instances[0]

        next_instance.active = True
        next_instance._key_pressed = True
