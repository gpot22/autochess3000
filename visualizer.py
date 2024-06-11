import pygame

pygame.init()
pygame.font.init()
vec2 = pygame.math.Vector2

import sys

from board import Grid
from pieces import Piece, PieceGroup
from utils import Globals

SCR_W, SCR_H  = 1200, 800
FPS = 60
TILE_W = 80

scr = pygame.display.set_mode((SCR_W, SCR_H))
clock = pygame.time.Clock()

piece_group = PieceGroup()

grid_offset = vec2((SCR_W - TILE_W*8)/2, (SCR_H - TILE_W*8)/2)

def draw_grid(grid):
    scr.blit(grid.surf, grid_offset)
    return grid_offset

def load_game(board, grid):
    for i, row in enumerate(board):
        for j, piece_id in enumerate(row):
            if not piece_id: continue
            p = Piece(piece_group, piece_id)
            p.set_grid(grid)
            p.move_to_tile(i, j)
            

def run(board):
    grid = Grid(TILE_W, grid_offset)
    load_game(board, grid)
    # p = Piece(piece_group, 'r')
    # p.move_to(vec2(280, 80))
    # p.set_grid(grid)
    
    run = True
        
    while run:
        scr.fill(pygame.Color('white')) # BG
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            #     pos = pygame.mouse.get_pos()
            #     print(pos)
                
            # if ev.type == pygame.MOUSEMOTION:
            #     pos = pygame.mouse.get_pos()
        
        draw_grid(grid)
        grid.update(events)
        piece_group.update(events)
        piece_group.draw_sprites()
        
        
        
        pygame.display.update()
        clock.tick(FPS)