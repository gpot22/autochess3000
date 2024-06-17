import pygame

pygame.init()
vec2 = pygame.math.Vector2

import sys

from board import Grid
from pieces import Piece, PieceGroup
from utils import Globals
from components import TextBox, Button, ComponentsGroup

SCR_W, SCR_H  = 1200, 800
FPS = 60
TILE_W = 80

scr = pygame.display.set_mode((SCR_W, SCR_H))
clock = pygame.time.Clock()

piece_group = PieceGroup()
components = ComponentsGroup()

grid_offset = vec2((SCR_W - TILE_W*8)/2, (SCR_H - TILE_W*8)/2)
print(f'{grid_offset=}')
def draw_grid(grid):
    scr.blit(grid.surf, grid_offset)
    return grid_offset

def load_game(board, grid):
    for i, row in enumerate(board):
        for j, piece_id in enumerate(row):
            if not piece_id.strip(): continue
            p = Piece(piece_group, piece_id, grid)
            p.move_to_tile(i, j)

def test_draw_right_arrow():
    x = 320
    y = 120
    total_l = 160
    
    arrowhead_total_w = 40
    arrowhead_l = 30
    
    line_w = 11
    line_l = total_l-arrowhead_l
    pygame.draw.line(scr, pygame.Color(Globals.COLOR_ANNOTATE), (x, y), (x+line_l, y), width=line_w)
    overhang_w = (arrowhead_total_w-line_w)/2
    arrowhead_points = [
        (x+line_l, y-overhang_w-line_w/2),
        (x+line_l, y+overhang_w +line_w/2),
        (x+line_l+arrowhead_l, y)
    ]
    pygame.draw.polygon(scr, pygame.Color(Globals.COLOR_ANNOTATE), arrowhead_points)
    pygame.draw.circle(scr, pygame.Color('purple'), (x, y), 2)
    
def load_components(stockfish):
    best_move_label = TextBox('', Globals.FONT1, 200, 10, 0, [2], txt_colour=pygame.Color('#016064'), group=components)
    
    best_move_btn_images = {
        'base': TextBox('Get Best Move', Globals.FONT1, border_w=1, padding=[5]).image,
        'hover': TextBox('Get Best Move', Globals.FONT1, border_w=2, padding=[5]).image,
        'click': TextBox('Get Best Move', Globals.FONT1, border_w=2, padding=[5], bg_colour=pygame.Color('gray')).image
    }
    Button(best_move_btn_images['base'], lambda: display_best_move(stockfish, best_move_label), x=10, y=10,
           hover_image=best_move_btn_images['hover'], click_image=best_move_btn_images['click'], group=components, click_cldwn=0.1)
            
def display_best_move(stockfish, label):
    best_move = stockfish.get_best_move()
    label.update_textbox(txt=best_move)
    
def run(board, stockfish):
    grid = Grid(TILE_W, grid_offset)
    load_game(board, grid)
    
    run = True
    
    load_components(stockfish)
    while run:
        scr.fill(pygame.Color('white')) # BG
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for p in piece_group.sprites():
                    p.selected = False
        
        draw_grid(grid)
        grid.update(events)
        piece_group.update(events)
        piece_group.draw_sprites()
        
        components.update()
        components.draw_sprites()
        
        
        pygame.display.update()
        clock.tick(FPS)