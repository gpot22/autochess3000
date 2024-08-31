import pygame
from styles import Styles
from cursor import cursor_state
from components import TextBox

vec2 = pygame.math.Vector2

class Grid(pygame.sprite.Group):
    def __init__(self, tile_w, offset, stockfish):
        pygame.sprite.Group.__init__(self)
        self.tile_w = tile_w
        self.offset = offset
        self.stockfish = stockfish
        
        self.surf = pygame.Surface((tile_w*8, tile_w*8))
        self.rect = pygame.Rect(self.offset.x, self.offset.y, tile_w*8, tile_w*8)
        self.label_squares = True
        self.tiles = self._build()
        
    
    def _build(self):
        tiles = []
        for i in range(8):
            row = []
            for j in range(8): # one row
                label = '' if not self.label_squares else f'{chr(j+ord('a'))}{8-i}'
                t = Tile(self, pygame.Rect(j*self.tile_w,i*self.tile_w, self.tile_w, self.tile_w), self._get_tile_colour(i, j), label)
                row.append(t)
                self.surf.blit(t.image, (t.rect.x, t.rect.y))
            tiles.append(row)
        return tiles

    def ij_to_xy(self, i, j, centre=False):
        x = self.offset.x + (j + 0.5*centre)*self.tile_w
        y = self.offset.y + (i + 0.5*centre)*self.tile_w
        return vec2(x, y)

    def xy_to_ij(self, x, y):
        i = (y - self.offset.y) // self.tile_w
        j = (x - self.offset.x) // self.tile_w
        return (int(i), int(j))
    
    def chess_coord_to_ij(self, coord):  # ex: a1 --> (7, 0)
        letter, number = coord.lower()
        j = ord(letter) - ord('a')
        i = 8 - int(number)
        return (i, j)
    
    def ij_to_chess_coord(self, i, j):
        letter = chr(j + ord('a'))
        number = f'{8 - i}'
        return f'{letter}{number}'
    
    def board_to_fen(self):
        fen_str = ''
        spaces = 0
        for row in self.tiles:
            for tile in row:
                if tile.piece is None:
                    spaces += 1
                else:
                    if spaces:
                        fen_str += str(spaces)
                        spaces = 0
                    fen_str += tile.piece.piece_id
            if spaces:
                fen_str += str(spaces)
                spaces = 0
            fen_str += '/'
        return fen_str[:-1] + ' w - - 0 20' # remove extra '/', + placeholder metadata
    
    def sync_stockfish_to_board(self):
        self.stockfish.set_fen_position(self.board_to_fen())
    def _get_tile_colour(self, i, j):
        return pygame.Color(Styles.COLOR_DARK) if (i+j)%2 else Styles.COLOR_LIGHT
    
    def update(self, events):
        super().update(events)
    #     for ev in events:
    #         if ev.type == pygame.MOUSEMOTION:
    #             if self.rect.collidepoint(pygame.mouse.get_pos()):
    #                 cursor_state['on_board'] = True
    #             else:
    #                 cursor_state['on_board'] = False

class Tile(pygame.sprite.Sprite):
    def __init__(self, grid, rect, colour, label=''):
        pygame.sprite.Sprite.__init__(self, grid)
        self.grid = grid
        self.rect = rect
        self.global_rect = pygame.Rect(rect.x + grid.offset.x, rect.y + grid.offset.y, rect.w, rect.h)
        self.base_colour = colour
        self.colour = colour
        self.image = pygame.Surface((self.rect.w, self.rect.w), pygame.SRCALPHA, 32).convert_alpha()
        self.label = label
        self._draw()
        
        self.hover = False
        self.piece = None
        
    def _draw(self):
        pygame.draw.rect(self.image, self.colour, pygame.Rect(0, 0, self.rect.w, self.rect.h))
        if self.label:
            tb = TextBox(self.label, Styles.FONTSMALL, padding=[2], txt_colour=pygame.Color('white'), bg_colour='transparent')
            w, h = tb.rect.w, tb.rect.h
            self.image.blit(tb.image, (self.rect.w/2-w/2, self.rect.h/2-h/2))
            
    def show_coords(self):
        x, y = self.global_rect.x, self.global_rect.y
        tb = TextBox(f'({x},{y})', Styles.FONT0, padding=[5], txt_colour=pygame.Color('purple'))
        w, h = tb.rect.w, tb.rect.h
        pygame.display.get_surface().blit(tb.image, (x+self.rect.w/2-w/2, y+self.rect.h/2-h/2))
    
    def piece_drag_highlight(self):
        x, y = self.global_rect.x, self.global_rect.y
        c = pygame.Color('gray')
        pygame.draw.rect(pygame.display.get_surface(), c, pygame.Rect(x, y, self.rect.w, self.rect.h), width=3)
    
    # def annotate(self):
    #     x, y = self.global_rect.x, self.global_rect.y
    #     w = self.rect.w
    #     c = pygame.Color(Styles.COLOR_ANNOTATE)
    #     pygame.draw.circle(pygame.display.get_surface(), c, vec2(x+w/2, y+w/2), w/2, 3)
    
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
            # self.show_coords()
            if cursor_state['dragging']:
                self.piece_drag_highlight()
        for ev in events:
            if ev.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if self.global_rect.collidepoint(pos):
                    self.hover = True
                else:
                    self.hover = False

class Annotation(pygame.sprite.Sprite): # TODO
    def __init__(self, group, grid, colour=Styles.COLOR_ANNOTATE):
        pygame.sprite.Sprite.__init__(self, group)
        self.grid = grid
        self.colour = colour
        
        self.start_tile = None
        self.end_tile = None
        
    def set_start_tile(self, i, j):
        self.start_tile = (i, j)
    
    def set_end_tile(self, i, j):
        self.end_tile = (i, j)
    
    def load_image(self):
        if self.start_tile is None: return
        
        if self.end_tile is None:  # thin circle
            self.image = pygame.Surface((self.grid.tile_w, self.grid.tile_w), pygame.SRCALPHA, 32).convert_alpha()
            self.rect = self.image.get_rect()
        elif self.start_tile == self.end_tile:  # thick circle
            self.image = pygame.Surface((self.grid.tile_w, self.grid.tile_w), pygame.SRCALPHA, 32).convert_alpha()
            self.rect = self.image.get_rect()
        else:  # arrow
            i = self.end_tile[0] - self.start_tile[0]  
            j = self.end_tile[1] - self.start_tile[1]          
            
            self.image = pygame.Surface((self.grid.tile_w * (abs(j)+1), self.grid.tile_w * (abs(i)+1)), pygame.SRCALPHA, 32).convert_alpha()
            self.rect = self.image.get_rect()
class AnnotationLayer(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.surf = pygame.display.get_surface()
    
    def draw_sprites(self):
        for sprite in self.sprites():
            self.surf.blit(sprite.image, sprite.rect)
        