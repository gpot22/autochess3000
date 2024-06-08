import pygame
from utils import Globals

class Grid:
    def __init__(self, tile_w):
        self.tile_w = tile_w
        self.surf = pygame.Surface((tile_w*8, tile_w*8))
        self.draw()
    
    # def build(self):
    #     return [[(i+j)%2 for i in range(8)] for j in range(8)]
    
    def draw(self):
        for i in range(8):
            for j in range(8):
                pygame.draw.rect(self.surf, self._get_tile_colour(i, j), pygame.Rect(i*self.tile_w, j*self.tile_w, self.tile_w, self.tile_w))
                
    def _get_tile_colour(self, i, j):
        return pygame.Color(Globals.COLOR_DARK) if (i+j)%2 else Globals.COLOR_LIGHT