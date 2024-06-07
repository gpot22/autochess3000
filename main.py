import pygame
import sys
from stockfish import Stockfish

pygame.init()
pygame.font.init()

SCR_W, SCR_H  = 900, 600
FPS = 60

scr = pygame.display.set_mode((SCR_W, SCR_H))
clock = pygame.time.Clock

def main():
    
    run = True
    while run:
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            

        pygame.display.update()
        clock.tick(FPS)
        
if __name__ == '__main__':
    main()