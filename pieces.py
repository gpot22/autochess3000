import pygame

class Piece(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.sprite_size = 64
        self.image
        
    def get_image(self, scale, flipX=False, flipY=False):
        image = pygame.image.load(self.image).convert_alpha()
        # Scale image
        image = pygame.transform.scale_by(image, scale)
        # Flip image
        if flipX or flipY:
            image = pygame.transform.flip(image, flipX, flipY)
        # Transparent pixels
        image.set_colorkey(self.colorkey)
        return image