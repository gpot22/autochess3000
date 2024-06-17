import pygame
import pygame.freetype

class Globals():
    COLOR_LIGHT = '#f0d9b5'
    COLOR_DARK = '#b58863'
    COLOR_SELECT = '#c69744aa'
    COLOR_ANNOTATE = '#1b8c39aa'
    FONT0 = pygame.freetype.SysFont('mono', 16, bold=True)
    FONT1 = pygame.freetype.SysFont('sans', 16)
    
cursor_state = {
    'dragging': False,
    'on_board': False,
    'annotating': False,
    'annotate_start': None
}
    