import pygame
import os
from spritesheet import SpriteSheet
from utils import cursor_state, Globals

PATH = os.path.dirname(__file__)

class Piece(pygame.sprite.Sprite):
    SPRITE_W = 300
    
    def __init__(self, group, piece_id):
        pygame.sprite.Sprite.__init__(self, group)
        self.piece_id =  piece_id
        spritesheet_image = pygame.image.load(os.path.join(PATH, 'assets/pieces.png'))
        self.spritesheet: SpriteSheet = SpriteSheet(spritesheet_image, self.SPRITE_W)
        self.load_sprite()
        # self.draw_hitbox()
        
        self.selected = False
        self.dragging = False
        
    # def get_piece_from_id(piece_id):
    
    def set_grid(self, grid):
        self.grid = grid
        self.i = 0
        self.j = 0
    
    def is_white(self):
        return self.piece_id.isupper()
        
    def load_sprite(self):
        ORDER = {'r': 0, 'b': 1, 'q': 2, 'k': 3, 'n': 4, 'p': 5}
        self.image = self.spritesheet.get_image(ORDER[self.piece_id.lower()], self.is_white(), scale=80/300, offset=(2, 50), spacing=(1, 75))
        self.rect = self.image.get_rect()
    
    def move_to(self, pos):
        self.rect.x = pos.x
        self.rect.y = pos.y
    
    def move_to_tile(self, i, j):
        self.i = i
        self.j = j
        pos = self.grid.ij_to_xy(i, j)
        self.move_to(pos)

    def draw_hitbox(self, colour=pygame.Color('blue'), width=2):
        pygame.draw.rect(self.image, colour, pygame.Rect(0, 0, self.rect.width, self.rect.height), width=width)
    
    def update(self, events):
        if self.selected and self.grid:
            self.grid.tiles[self.i][self.j].set_colour(Globals.COLOR_SELECT)
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(pos):
                    self.selected = True
                    self.dragging = True
                    cursor_state['dragging'] = True
                    
                
            if ev.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if self.dragging:
                    self.rect.center = pos
                    
            
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                pos = pygame.mouse.get_pos()
                if self.dragging:
                    self.dragging = False
                    cursor_state['dragging'] = False
                    if cursor_state['on_board']:
                        self.move_to_tile(*self.grid.xy_to_ij(pos[0], pos[1]))
                    else:
                        self.move_to_tile(self.i, self.j)

class PieceGroup(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.surf = pygame.display.get_surface()
    
    def draw_sprites(self):
        for sprite in self.sprites():
            self.surf.blit(sprite.image, sprite.rect)
        
    