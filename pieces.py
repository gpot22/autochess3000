import pygame
import os
from spritesheet import SpriteSheet

PATH = os.path.dirname(__file__)

class Piece(pygame.sprite.Sprite):
    SPRITE_W = 300
    PIECES = {
        'rook': 0,
        'bishop': 1,
        'queen': 2,
        'king': 3,
        'knight': 4,
        'pawn': 5
    }
    def __init__(self, piece, is_white):
        pygame.sprite.Sprite.__init__(self)
        spritesheet_image = pygame.image.load(os.path.join(PATH, 'assets/pieces.png'))
        self.spritesheet: SpriteSheet = SpriteSheet(spritesheet_image, self.SPRITE_W)
        self.load_sprite(self.PIECES[piece], is_white)
        
    def load_sprite(self, piece_id, is_white):
        self.image = self.spritesheet.get_image(piece_id, is_white, scale=80/300, offset=(2, 50), spacing=(1, 75))
        self.rect = self.image.get_rect()
    