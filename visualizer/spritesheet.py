import pygame

class SpriteSheet():
    def __init__(self, image, frame_size, transparent_color=(77, 77, 77)):
        self.sheet = image
        self.size = frame_size
        self.colorkey = transparent_color
    
    def get_image(self, frameX, frameY, scale=1, flipX=False, flipY=False, offset=(0, 0), spacing=(0, 0)):
        image = pygame.Surface((self.size, self.size), pygame.SRCALPHA, 32).convert_alpha()
        image.blit(self.sheet, (0, 0), area=(frameX*(self.size + spacing[0]) + offset[0], frameY*(self.size + spacing[1]) + offset[1], self.size, self.size))
        # Scale image
        image = pygame.transform.smoothscale_by(image, scale)
        # Flip image
        if flipX or flipY:
            image = pygame.transform.flip(image, flipX, flipY)
        # Transparent pixels
        image.set_colorkey(self.colorkey)
        return image