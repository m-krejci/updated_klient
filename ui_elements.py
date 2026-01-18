import pygame
from constants import *


class UI:
    def __init__(self, screen, font, font_small):
        self.screen = screen
        self.font = font
        self.small_font = font_small

    def draw_button(self, rect, text, mouse_pos, hover_color=BUTTON_HOVER, button_color=BUTTON_COLOR):
        is_hover = rect.collidepoint(mouse_pos)
        color = hover_color if is_hover else button_color

        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        pygame.draw.rect(self.screen, (50,50,50), rect, 2, border_radius=5)

        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

        return is_hover
    
    def draw_error(self, rect, message):
        if not message:
            return
        
        error_surface = self.small_font.render(message, True, (200, 0, 0))
        self.screen.blit(error_surface, (rect.x + 5, rect.bottom + 5))

    def draw_input(self, rect, text, is_active):
        bg_color = (230, 240, 255) if is_active else (255, 255, 255)
        border_color = (0, 120, 255) if is_active else (100, 100, 100)

        pygame.draw.rect(self.screen, bg_color, rect, border_radius=6)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=6)