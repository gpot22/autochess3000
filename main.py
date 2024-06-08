import pygame
import sys

pygame.init()
pygame.font.init()

from stockfish import Stockfish
from board import Grid
from pieces import Piece

SCR_W, SCR_H  = 1200, 800
FPS = 60
TILE_W = 80

scr = pygame.display.set_mode((SCR_W, SCR_H))
clock = pygame.time.Clock()

def main():
    grid = Grid(TILE_W)
    p = Piece('rook', False)
    
    run = True
    while run:
        scr.fill(pygame.Color('white'))
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        scr.blit(grid.surf, ((SCR_W - TILE_W*8)/2, (SCR_H - TILE_W*8)/2))
        scr.blit(p.image, (200, 200))
        s = pygame.Surface((500, 500), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(s, pygame.Color('blue'), p.rect, width=3)
        scr.blit(s, (200, 200))
        
        # pygame.draw.rect(scr, pygame.Color('blue'), p.rect)
        pygame.display.update()
        clock.tick(FPS)
        
if __name__ == '__main__':
    main()