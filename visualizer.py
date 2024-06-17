import pygame

pygame.init()
vec2 = pygame.math.Vector2

import sys

from board import Grid
from pieces import Piece, PieceGroup
from utils import Globals
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
        print(f'{self.grid_offset=}')
        
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
            'base': TextBox(txt, Globals.FONT1, border_w=1, padding=[5], border_r=3).image,
            'hover': TextBox(txt, Globals.FONT1, border_w=2, padding=[5], border_r=3).image,
            'click': TextBox(txt, Globals.FONT1, border_w=2, padding=[5], bg_colour=pygame.Color('gray'), border_r=3).image
        }
        return Button(btn_images['base'], on_click, x=x, y=y,
            hover_image=btn_images['hover'], click_image=btn_images['click'], group=self.components, click_cldwn=0.1)
                
    def load_components(self, stockfish):
        best_move_label = TextBox('', Globals.FONT1, x=200, y=10, padding=[2], txt_colour=pygame.Color('#016064'), group=self.components)
        self.simple_btn('Get Best Move', lambda: self.display_best_move(stockfish, best_move_label), x=10, y=10)
        self.simple_btn('Get FEN', lambda: print(stockfish.get_fen_position()), x=10, y=30)
        ToggleSwitch(50, 20, x=50, y=200, group=self.components)
        

    def display_best_move(self, stockfish, label):
        best_move = stockfish.get_best_move()
        label.update_textbox(txt=best_move)
    
    def run(self, board):
        grid = Grid(self.TILE_W, self.grid_offset, self.stockfish)
        self.load_game(board, grid)
        print(grid.board_to_fen())
        run = True
        
        self.load_components(self.stockfish)
        while run:
            self.scr.fill(pygame.Color('white')) # BG
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    for p in self.piece_group.sprites():
                        p.selected = False
            
            self.draw_grid(grid)
            grid.update(events)
            self.piece_group.update(events)
            self.piece_group.draw_sprites()
            
            self.components.update()
            self.components.draw_sprites()
            
            
            pygame.display.update()
            self.clock.tick(self.FPS)