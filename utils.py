import pygame

class Globals():
    COLOR_LIGHT = '#f0d9b5'
    COLOR_DARK = '#b58863'
    COLOR_SELECT = '#c69744aa'
    FONT1 = pygame.font.SysFont('mono', 16, bold=True)
    
cursor_state = {
    'dragging': False,
    'on_board': False
}
    