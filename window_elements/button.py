import pygame
import os

from src.helpers import play_on_empty


class Button:
    def __init__(
        self,
        image,
        pos,
        text_input,
        font,
        base_color,
        hovering_color,
        image_highlited=None,
    ):
        self.image = image
        if image_highlited:
            self.image_highlighted = image_highlited
        else:
            self.image_highlighted = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        for index in range(0, 8):
            if not pygame.mixer.Channel(index).get_busy():
                self.channel_index = index

    def update(self, screen, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom):
            if self.image_highlighted is not None:
                screen.blit(self.image_highlighted, self.rect)
        else:
            if self.image is not None:
                screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom):
            self.channel_index = play_on_empty("resources/button_click.wav")
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
