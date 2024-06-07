import pygame

class SpriteSheet():
    def __init__(self, image, frame_size, transparent_color=(0,0,0)):
        self.sheet = image
        self.size = frame_size
        self.colorkey = transparent_color
    
    def get_image(self, frameX, frameY, scale, flipX=False, flipY=False):
        image = pygame.Surface((self.size, self.size)).convert_alpha()
        image.blit(self.sheet, (0, 0), area=(frameX*self.size, frameY*self.size, self.size, self.size))
        # Scale image
        image = pygame.transform.scale_by(image, scale)
        # Flip image
        if flipX or flipY:
            image = pygame.transform.flip(image, flipX, flipY)
        # Transparent pixels
        image.set_colorkey(self.colorkey)
        return image