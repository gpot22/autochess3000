import pygame
from utils import Globals, cursor_state

vec2 = pygame.math.Vector2

class Grid(pygame.sprite.Group):
    def __init__(self, tile_w, offset):
        pygame.sprite.Group.__init__(self)
        self.tile_w = tile_w
        self.offset = offset
        self.surf = pygame.Surface((tile_w*8, tile_w*8))
        self.rect = pygame.Rect(self.offset.x, self.offset.y, tile_w*8, tile_w*8)
        self.tiles = self._build()
    
    def _build(self):
        tiles = []
        for i in range(8):
            r = []
            for j in range(8):
                t = Tile(self, pygame.Rect(j*self.tile_w,i*self.tile_w, self.tile_w, self.tile_w), self._get_tile_colour(i, j))
                r.append(t)
                self.surf.blit(t.image, (t.rect.x, t.rect.y))
            tiles.append(r)
        return tiles

    def ij_to_xy(self, i, j):
        x = self.offset.x + j*self.tile_w
        y = self.offset.y + i*self.tile_w
        return vec2(x, y)

    def xy_to_ij(self, x, y):
        i = (y - self.offset.y) // self.tile_w
        j = (x - self.offset.x) // self.tile_w
        return (int(i), int(j))
                
    def _get_tile_colour(self, i, j):
        return pygame.Color(Globals.COLOR_DARK) if (i+j)%2 else Globals.COLOR_LIGHT
    
    def update(self, events):
        super().update(events)
        for ev in events:
            if ev.type == pygame.MOUSEMOTION:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    cursor_state['on_board'] = True
                else:
                    cursor_state['on_board'] = False

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
        c = pygame.Color('gray')
        pygame.draw.rect(pygame.display.get_surface(), c, pygame.Rect(x, y, self.rect.w, self.rect.h), width=3)
    
    def set_colour(self, colour):
        self.colour = colour
        self._draw()
        pygame.display.get_surface().blit(self.image, self.global_rect)
    
    def reset_colour(self):
        self.colour = self.base_colour
        self._draw()
        pygame.display.get_surface().blit(self.image, self.global_rect)
    
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
                else:
                    self.hover = False