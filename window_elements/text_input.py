import pygame


class TextInput:
    _id = 0
    _instances = []
    _tab_pressed = False
    _enter_pressed = False
    _backspace_pressed = False
    _time_constant = 100

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        text: str = "",
        text_color: pygame.Color = pygame.Color("black"),
        fill_inactive: pygame.Color = pygame.Color("gray"),
        fill_active: pygame.Color = pygame.Color("white"),
        font_size: int = 20,
        is_active: bool = False,
    ):
        self.id = TextInput._id
        self.rect = pygame.Rect(x, y, w, h)
        self.text_color = text_color
        self.fill_inactive = fill_inactive
        self.fill_active = fill_active
        self.hidden_text = text
        self.text = text
        self.FONT = pygame.font.Font("resources/ASansrounded.ttf", font_size)
        self.txt_surface = self.FONT.render(text, True, self.text_color)
        self.active = is_active
        self.last_backspace_time = 0

        TextInput._id += 1
        TextInput._instances.append(self)

    def delete_instance(self):
        if self in TextInput._instances:
            TextInput._instances.remove(self)

        if not TextInput._instances:
            TextInput._id = 0

    def event(self, event, hide_text=False):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = False
            if self.rect.collidepoint(event.pos):
                self.active = True

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self._backspace_pressed = True
                elif event.key == pygame.K_TAB:
                    if not self._tab_pressed:
                        self.jump_to_next_input()
                elif event.key == pygame.K_RETURN:
                    TextInput._enter_pressed = True
                elif event.key == pygame.K_ESCAPE:
                    self.active = False
                else:
                    if hide_text:
                        self.text += "*"
                        self.hidden_text += event.unicode
                    else:
                        self.text += event.unicode
                self.txt_surface = self.FONT.render(self.text, True, self.text_color)

        if event.type == pygame.KEYUP:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self._backspace_pressed = False
                for instance in TextInput._instances:
                    instance._tab_pressed = False
                    TextInput._enter_pressed = False

    def get_string(self):
        if len(self.text) == len(self.hidden_text):
            return self.hidden_text
        return self.text

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.active and self._backspace_pressed:
            if current_time - self.last_backspace_time > TextInput._time_constant:
                if self.text:
                    self.text = self.text[:-1]
                    if self.hidden_text:
                        self.hidden_text = self.hidden_text[:-1]
                    self.txt_surface = self.FONT.render(
                        self.text, True, self.text_color
                    )
                self.last_backspace_time = current_time

    def draw(self, screen):
        # Fill the rect with the fill color based on active status
        fill_color = self.fill_active if self.active else self.fill_inactive
        pygame.draw.rect(screen, fill_color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.text_color, self.rect, 2)

    def jump_to_next_input(self):
        self.active = False
        self._tab_pressed = False
        next_id = self.id + 1

        next_instance = None
        for instance in TextInput._instances:
            if instance.id == next_id:
                next_instance = instance
                break
        if not next_instance:
            next_instance = TextInput._instances[0]

        next_instance.active = True
        next_instance._tab_pressed = True

    def set_active(self, screen):
        self.active = True
        self.draw(screen)
