import pygame
import pygame.freetype

class Styles():
    COLOR_LIGHT = '#f0d9b5'
    COLOR_DARK = '#b58863'
    COLOR_SELECT = '#c69744aa'
    COLOR_ANNOTATE = '#1b8c39aa'
    FONTSMALL = pygame.freetype.SysFont('mono', 12, bold=False)
    FONT0 = pygame.freetype.SysFont('mono', 16, bold=True)
    FONT1 = pygame.freetype.SysFont('sans', 16)
    FONT1BIG = pygame.freetype.SysFont('sans', 30)
    