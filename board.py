import pygame
from utils import Globals, cursor_state

class Grid(pygame.sprite.Group):
    def __init__(self, tile_w, offset):
        pygame.sprite.Group.__init__(self)
        self.tile_w = tile_w
        self.offset = offset
        self.surf = pygame.Surface((tile_w*8, tile_w*8))
        # self._draw()
        self.tiles = self._build()
    
    def _build(self):
        tiles = []
        for i in range(8):
            for j in range(8):
                t = Tile(self, pygame.Rect(i*self.tile_w, j*self.tile_w, self.tile_w, self.tile_w), self._get_tile_colour(i, j))
                tiles.append(t)
                self.surf.blit(t.image, (t.rect.x, t.rect.y))
        return tiles
                
    def _get_tile_colour(self, i, j):
        return pygame.Color(Globals.COLOR_DARK) if (i+j)%2 else Globals.COLOR_LIGHT
    
    def update(self, events):
        super().update(events)
        for t in self.tiles:
            self.surf.blit(t.image, (t.rect.x, t.rect.y))

class Tile(pygame.sprite.Sprite):
    def __init__(self, grid, rect, colour):
        pygame.sprite.Sprite.__init__(self, grid)
        self.rect = rect
        self.global_rect = pygame.Rect(rect.x + grid.offset.x, rect.y + grid.offset.y, rect.w, rect.h)
        self.base_colour = colour
        self.colour = colour
        self.image = pygame.Surface((self.rect.w, self.rect.w), pygame.SRCALPHA, 32).convert_alpha()
        self._draw()
        self.hover = False
        
    def _draw(self):
        pygame.draw.rect(self.image, self.colour, pygame.Rect(0, 0, self.rect.w, self.rect.h))
    
    def show_coords(self):
        x, y = self.global_rect.x, self.global_rect.y
        pygame.draw.circle(pygame.display.get_surface(), pygame.Color('purple'), (x, y), 4)
        txt = f'({x},{y})'
        w, h = Globals.FONT1.size(txt)
        txt_surf = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
        txt_render = Globals.FONT1.render(txt, False, pygame.Color('purple'))
        txt_surf.fill(pygame.Color('white'))
        pygame.draw.rect(txt_surf, pygame.Color('gray'), pygame.Rect(0, 0, w, h), width=1)
        txt_surf.blit(txt_render, (0, 0))
        pygame.display.get_surface().blit(txt_surf, (x+self.rect.w/2-w/2, y+self.rect.h/2-h/2))
    
    def highlight(self):
        x, y = self.global_rect.x, self.global_rect.y
        # c = pygame.Color(255, 255, 255, 40)
        c = pygame.Color('gray')
        pygame.draw.rect(pygame.display.get_surface(), c, pygame.Rect(x, y, self.rect.w, self.rect.h), width=3)
        
    
    def update(self, events):
        super().update()
        if self.hover:
            self.show_coords()
            if cursor_state['dragging']:
                self.highlight()
        for ev in events:
            if ev.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if self.global_rect.collidepoint(pos):
                    self.hover = True
                    # self.show_coords()
                else:
                    self.hover = False