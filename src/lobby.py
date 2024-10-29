from src.global_vars import load_initial_window_setting
from src.button import Button

import pygame
import sys
import os

class H5_Lobby():
    def __init__(self):
        pygame.init()
        config = load_initial_window_setting()

        self.SCREEN = pygame.display.set_mode((config["screen_width"], config["screen_hight"])) 
        self.BG = pygame.image.load(os.path.join(os.getcwd(), "resources/h5_background.jpg"))
        pygame.display.set_caption("Menu")

    def get_font(self, font_size: int = 75):
        return pygame.font.Font("resources/font.ttf", font_size)

    def main_menu(self):
        while True:
            self.SCREEN.blit(self.BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = self.get_font(30).render("H5 Lobby Launcher", True, "#b68f40")
            MENU_RECT = MENU_TEXT.get_rect(center=(290, 220))

            PLAY_BUTTON = Button(image=pygame.image.load(os.path.join(os.getcwd(), "resources/rectangle.png")), pos=(290, 350), 
                                text_input="PLAY", font=self.get_font(75), base_color="#d7fcd4", hovering_color="White")
            OPTIONS_BUTTON = Button(image=pygame.image.load(os.path.join(os.getcwd(), "resources/rectangle.png")), pos=(290, 500), 
                                text_input="OPTIONS", font=self.get_font(75), base_color="#d7fcd4", hovering_color="White")
            QUIT_BUTTON = Button(image=pygame.image.load(os.path.join(os.getcwd(), "resources/rectangle.png")), pos=(290, 650), 
                                text_input="QUIT", font=self.get_font(75), base_color="#d7fcd4", hovering_color="White")

            self.SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()
    
    def run_game(self):
        self.main_menu()