import pygame

pygame.init()
vec2 = pygame.math.Vector2

import sys

from chessboard import Grid
from pieces import Piece, PieceGroup
from styles import Styles
from components import TextBox, Button, ComponentGroup, ToggleSwitch

class Visualizer:
    SCR_W, SCR_H  = 1200, 800
    FPS = 60
    TILE_W = 80

    def __init__(self, stockfish):
        self.stockfish = stockfish
        
        self.scr = pygame.display.set_mode((self.SCR_W, self.SCR_H))
        self.clock = pygame.time.Clock()
        
        self.piece_group = PieceGroup()
        self.components = ComponentGroup()

        self.grid_offset = vec2((self.SCR_W - self.TILE_W*8)/2, (self.SCR_H - self.TILE_W*8)/2)
        
    def draw_grid(self, grid):
        self.scr.blit(grid.surf, self.grid_offset)
    
    def load_game(self, board, grid):
        for i, row in enumerate(board):
            for j, piece_id in enumerate(row):
                if not piece_id.strip(): continue
                p = Piece(self.piece_group, piece_id, grid)
                p.move_to_tile(i, j, init=True)
                
    def simple_btn(self, txt, on_click, x=0, y=0):
        btn_images = {
            'base': TextBox(txt, Styles.FONT1, border_w=1, padding=[5], border_r=3).image,
            'hover': TextBox(txt, Styles.FONT1, border_w=2, padding=[5], border_r=3).image,
            'click': TextBox(txt, Styles.FONT1, border_w=2, padding=[5], bg_colour=pygame.Color('gray'), border_r=3).image
        }
        return Button(btn_images['base'], on_click, x=x, y=y,
            hover_image=btn_images['hover'], click_image=btn_images['click'], group=self.components, click_cldwn=0.1)
                
    def load_components(self, stockfish):
        turn_label = TextBox(f'{"White" if self.meta_data['turn_colour'] == "w" else "Black"} To Move', Styles.FONT1BIG, x='center', y=30, origin='center',padding=[4], bg_colour='transparent', txt_colour=pygame.Color('Purple'), group=self.components)
        best_move_label = TextBox('', Styles.FONT1, x=200, y=10, padding=[2], txt_colour=pygame.Color('#016064'), group=self.components)
        self.simple_btn('Get Best Move', lambda: self.display_best_move(stockfish, best_move_label), x=10, y=10)
        self.simple_btn('Get FEN', lambda: print(stockfish.get_fen_position()), x=10, y=30)
        ToggleSwitch(50, 20, x=50, y=200, group=self.components)
        

    def display_best_move(self, stockfish, label):
        best_move = stockfish.get_best_move()
        label.update_textbox(txt=best_move)
    
    def run(self, board, meta_data):
        grid = Grid(self.TILE_W, self.grid_offset, self.stockfish)
        self.load_game(board, grid)
        self.meta_data = meta_data
        print(grid.board_to_fen())
        run = True
        
        arrow_on = False
        active_arrow = None
        annotation_layer = pygame.Surface((self.SCR_W, self.SCR_H)).convert_alpha()
        annotation_layer.set_colorkey((0, 0, 0))
        annotation_group = AnnotationGroup(annotation_layer)
        self.load_components(self.stockfish)
        while run:
            self.scr.fill(pygame.Color('white')) # BG
            annotation_layer.fill((0, 0, 0))
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        for p in self.piece_group.sprites():
                            p.selected = False
                    if ev.button == 3:
                        pos = pygame.mouse.get_pos()
                        if arrow_on:
                            active_arrow.final(pos)
                            annotation_group.add(active_arrow)
                            active_arrow = None
                        else:
                            active_arrow = Arrow(annotation_layer, pos)
                        arrow_on = not arrow_on
            
            self.draw_grid(grid)
            grid.update(events)
            self.piece_group.update(events)
            self.piece_group.draw_sprites()
            
            self.components.update()
            self.components.draw_sprites()
            
            if active_arrow is not None:
                active_arrow.update(pygame.mouse.get_pos())
            self.test_draw_right_arrow()
           
            annotation_group.draw_sprites()
            self.scr.blit(annotation_layer, (0, 0))
            
            pygame.display.update()
            self.clock.tick(self.FPS)
            
    def test_draw_right_arrow(self):
        x = 320
        y = 120
        total_l = 160
        
        arrowhead_total_w = 40
        arrowhead_l = 30
        
        line_w = 11
        line_l = total_l-arrowhead_l
        pygame.draw.line(self.scr, pygame.Color(Styles.COLOR_ANNOTATE), (x, y), (x+line_l, y), width=line_w)
        overhang_w = (arrowhead_total_w-line_w)/2
        arrowhead_points = [
            (x+line_l, y-overhang_w-line_w/2),
            (x+line_l, y+overhang_w +line_w/2),
            (x+line_l+arrowhead_l, y)
        ]
        pygame.draw.polygon(self.scr, pygame.Color(Styles.COLOR_ANNOTATE), arrowhead_points)
        pygame.draw.circle(self.scr, pygame.Color('purple'), (x, y), 2)
        
class Arrow(pygame.sprite.Sprite):
    def __init__(self, surf, start):
        pygame.sprite.Sprite.__init__(self)
        self.start = start
        
        self.surf = surf
        self.colour = pygame.Color(Styles.COLOR_ANNOTATE)
        self.line_w = 11
        
    def update(self, pos=None):
        if pos is None: return
        pygame.draw.line(self.surf, self.colour, self.start, pos, self.line_w)
        
    def final(self, pos):
        dx = pos[0] - self.start[0]
        dy = pos[1] - self.start[1]
        self.image = pygame.Surface((abs(dx), abs(dy)))
        x = 0 if pos[0] > self.start[0] else self.start[0] - pos[0]
        y = 0 if pos[1] > self.start[1] else self.start[1] - pos[1]
        self.rect = self.image.get_rect()
        if pos[0] > self.start[0]:
            self.rect.left = self.start[0]
        else:
            self.rect.right = self.start[0]
        
        if pos[1] > self.start[1]:
            self.rect.top = self.start[1]
        else:
            self.rect.bottom = self.start[1]
        
        # self.surf.fill((0, 0, 0))
        pygame.draw.line(self.image, self.colour, (x, y), (x+dx, y+dy), self.line_w)
    
class AnnotationGroup(pygame.sprite.Group):
    def __init__(self, surf):
        pygame.sprite.Group.__init__(self)
        self.surf = surf
        
    def update(self):
        super().update()
        
    def draw_sprites(self):
        for sprite in self.sprites():
            self.surf.blit(sprite.image, sprite.rect)