import pygame
from collections import deque
from datetime import datetime

class Console:
    """Console pro zobrazení chybových či potvrzovacích zpráv
    """
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font, max_lines: int = 3, bg_color=(0, 0, 0), 
                 okay_text_color = (0, 255, 0), error_text_color=(255,0,0), padding:int=5):
        self.rect = rect
        self.font = font
        self.max_lines = max_lines
        self.bg_color = bg_color
        self.okay_text_color = okay_text_color
        self.error_text_color = error_text_color
        self.padding = padding

        self.lines = deque(maxlen=max_lines)

    def log(self, text:str, error:bool):
        """_summary_

        Args:
            text (str): Text k zobrazení
            error (bool): Boolean k rozhodnutí barvy
        """
        self.lines.append([f"[{datetime.now().strftime('%H:%M:%S')}] {str(text)}", error])

    def draw(self, surface: pygame.Surface):
        """ Vykresluje zprávy na obrazovku

        Args:
            surface (pygame.Surface): Plocha k vykreslení
        """
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=15)

        y = self.rect.y + self.padding
        for line in self.lines:
            error = line[1]
            text = line[0]
            if error:
                text_surf = self.font.render(text, True, self.error_text_color)
            else:
                text_surf = self.font.render(text, True, self.okay_text_color)

            surface.blit(text_surf, (self.rect.x + self.padding, y))
            y += self.font.get_height()
    
    def delete(self):
        """Odstranění zpráv ve struktuře
        """
        self.lines = deque(maxlen=self.max_lines)
        