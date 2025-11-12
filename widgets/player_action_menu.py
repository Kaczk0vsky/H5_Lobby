import pygame
import os

from src.helpers import play_on_empty_channel, render_small_caps


class PlayerActionMenu:
    def __init__(
        self,
        position: tuple[float, float],
        dimensions: tuple[int, int],
        color: pygame.Color,
        hovering_color: pygame.Color,
        inactive_color: pygame.Color,
        font_size: int,
        state: str,
    ):
        self.w = dimensions[0]
        self.h = dimensions[1]
        self.color = color
        self.hovering_color = hovering_color
        self.inactove_color = inactive_color
        self.font_size = font_size
        self.state = state
        self.rect = pygame.Rect(position, dimensions)
        self.bg = pygame.image.load(os.path.join(os.getcwd(), "resources/player_action_menu/frame_bg.png"))
        self.chat_icon = pygame.image.load(os.path.join(os.getcwd(), "resources/player_action_menu/chat_icon.png"))
        self.invite_icon = pygame.image.load(os.path.join(os.getcwd(), "resources/player_action_menu/invite_icon.png"))
        self.line = pygame.image.load(os.path.join(os.getcwd(), "resources/frames_and_bg/separating_stripe.png"))
        self.uncheck_mark = pygame.image.load(os.path.join(os.getcwd(), "resources/registration/no2.png"))
        self.uncheck_mark_highlighted = pygame.image.load(os.path.join(os.getcwd(), "resources/registration/no1.png"))

        self.bg = pygame.transform.scale(self.bg, (self.w, self.h))
        self.check_mark_rect = pygame.Rect((self.w * 0.2, self.h * 0.1), (self.h * 0.125, self.h * 0.125))
        self.uncheck_mark = pygame.transform.scale(self.uncheck_mark, (self.check_mark_rect.width, self.check_mark_rect.height))
        self.uncheck_mark_highlighted = pygame.transform.scale(
            self.uncheck_mark_highlighted, (self.check_mark_rect.width, self.check_mark_rect.height)
        )
        self.text_surface_invite = render_small_caps("Invite to game", self.font_size, self.color)
        self.text_surface_invite_highlighted = render_small_caps("Invite to game", self.font_size, self.hovering_color)
        self.text_surface_invite_inactive = render_small_caps("Invite to game", self.font_size, self.inactove_color)
        self.text_surface_message = render_small_caps("Send message", self.font_size, self.color)
        self.text_surface_message_highlighted = render_small_caps("Send message", self.font_size, self.hovering_color)

        self.is_visible = False
        self.ignore_next_click = False

    def update(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        check_x = self.rect.x + self.w - self.check_mark_rect.width - self.w * 0.075
        check_y = self.rect.y + self.h * 0.1125
        self.check_mark_rect.topleft = (check_x, check_y)

        if self.is_visible:
            screen.blit(self.bg, (self.rect.x, self.rect.y))

            # --- ICON SCALLING ---
            icon_size = int(self.h * 0.15)
            invite_icon_scaled = pygame.transform.scale(self.invite_icon, (icon_size, icon_size))
            chat_icon_scaled = pygame.transform.scale(self.chat_icon, (icon_size, icon_size))

            # --- INVITE TO GAME ---
            self.invite_rect = self.text_surface_invite.get_rect()
            self.invite_rect.centerx = self.rect.x + self.w / 2
            self.invite_rect.top = self.rect.y + self.h * 0.15
            invite_icon_rect = invite_icon_scaled.get_rect()
            invite_icon_rect.centery = self.invite_rect.centery
            invite_icon_rect.right = self.invite_rect.left - self.w * 0.03

            if self.state == "Online":
                if self.invite_rect.collidepoint(mouse_pos):
                    screen.blit(self.text_surface_invite_highlighted, self.invite_rect)
                else:
                    screen.blit(self.text_surface_invite, self.invite_rect)
            else:
                screen.blit(self.text_surface_invite_inactive, self.invite_rect)

            screen.blit(invite_icon_scaled, invite_icon_rect)

            # --- TEXT LINE ---
            line_scaled = pygame.transform.scale(self.line, (int(self.w * 0.85), int(self.h * 0.015)))
            line_rect = line_scaled.get_rect()
            line_rect.centerx = self.rect.x + self.w / 2
            line_rect.top = self.invite_rect.bottom + self.h * 0.02
            screen.blit(line_scaled, line_rect)

            # --- SEND MESSAGE ---
            self.message_rect = self.text_surface_message.get_rect()
            self.message_rect.centerx = self.rect.x + self.w / 2
            self.message_rect.top = line_rect.bottom + self.h * 0.025
            chat_icon_rect = chat_icon_scaled.get_rect()
            chat_icon_rect.centery = self.message_rect.centery
            chat_icon_rect.right = self.message_rect.left - self.w * 0.03

            if self.message_rect.collidepoint(mouse_pos):
                screen.blit(self.text_surface_message_highlighted, self.message_rect)
            else:
                screen.blit(self.text_surface_message, self.message_rect)

            screen.blit(chat_icon_scaled, chat_icon_rect)

            # --- TEXT LINE ---
            line_scaled = pygame.transform.scale(self.line, (int(self.w * 0.85), int(self.h * 0.015)))
            line_rect = line_scaled.get_rect()
            line_rect.centerx = self.rect.x + self.w / 2
            line_rect.top = self.message_rect.bottom + self.h * 0.02
            screen.blit(line_scaled, line_rect)

            # --- CHECK MARK ---
            if self.check_mark_rect.collidepoint(mouse_pos):
                screen.blit(self.uncheck_mark_highlighted, self.check_mark_rect.topleft)
            else:
                screen.blit(self.uncheck_mark, self.check_mark_rect.topleft)

    def event(self, event, mouse_pos: tuple[int, int]) -> None:
        if self.ignore_next_click:
            self.ignore_next_click = False
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_visible:
            if self.check_mark_rect.collidepoint(mouse_pos):
                play_on_empty_channel(path="resources/button_click.mp3")
                self.is_visible = False
            elif not self.rect.collidepoint(mouse_pos):
                self.is_visible = False
            elif self.invite_rect.collidepoint(mouse_pos) and self.state == "Online":
                play_on_empty_channel(path="resources/button_click.mp3")
                self.is_visible = False
                return "invite_player"
            elif self.message_rect.collidepoint(mouse_pos):
                play_on_empty_channel(path="resources/button_click.mp3")
                self.is_visible = False
                return "send_message"
