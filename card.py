import pygame

class Card:
    def __init__(self, name, image, x, y):
        self.name = name
        self.image = image
        self.rect: pygame.Rect = image.get_rect(topleft=(x,y))
        self.selected = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.selected:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 3)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.selected = not self.selected

    def unselect(self):
        self.selected = not self.selected

    def get_state(self):
        return self.selected