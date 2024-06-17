import pygame
import re
from threading import Timer
vec2 = pygame.math.Vector2

class TextBox(pygame.sprite.Sprite):
    '''
    padding rules
    - None/False => no padding
    - 1-item list [a] => padding for all set to `a`
    - 2-item list [v, h] => padding for top & bottom set to `v`, padding for left & right set to `h`
    - 4-item list [t, r, b, l] => yes
    '''
    def __init__(self, txt, font, x=0, y=0, border_w=0, border_r=0, padding=None, txt_colour=pygame.Color('black'), bg_colour=pygame.Color('white'), border_colour=pygame.Color('gray'), group=None):
        if isinstance(group, pygame.sprite.Group):
            pygame.sprite.Sprite.__init__(self, group)
        else:
            pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.txt = txt
        self.font = font
        self.border_w = border_w
        self.border_r = border_r
        self.padding = padding
        self.txt_colour = txt_colour
        self.bg_colour = bg_colour
        self.border_colour = border_colour
        
        self.update_textbox()
        # self.update_textbox(txt, font, border_w, padding, txt_colour, bg_colour, border_colour)
        
        self.offset = vec2(0, 0)
    
        
    def update_textbox(self, txt=-1, font=-1, border_w=-1, border_r=-1, padding=-1, txt_colour=-1, bg_colour=-1, border_colour=-1):
        # update attrs as necessary - idk a better way to do this lol
        if txt != -1: self.txt = txt
        if font != -1: self.font = font
        if border_w != -1: self.border_w = border_w
        if border_r != -1: self.border_r = border_r
        if padding != -1: self.padding = padding
        if txt_colour != -1: self.txt_colour = txt_colour
        if bg_colour != -1: self.bg_colour = bg_colour
        if border_colour != -1: self.border_colour = border_colour
        # update textbox sprite
        txt_rect = self.get_txt_rect(self.txt, self.font, self.padding)
        w, h = txt_rect.w, txt_rect.h
        self.image = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        # self.image.fill(self.bg_colour)
        pygame.draw.rect(self.image, self.bg_colour, pygame.Rect(0, 0, w, h), border_radius=self.border_r)
        if self.border_w > 0:
            pygame.draw.rect(self.image, self.border_colour, pygame.Rect(0, 0, w, h), width=self.border_w, border_radius=self.border_r)
        self.font.render_to(self.image, txt_rect.topleft, self.txt, self.txt_colour)
        
    def move_to(self, x, y):
        self.x = self.rect.x = x
        self.y = self.rect.y = y

        
    def get_txt_rect(self, txt, font, padding):
        txt_rect = font.get_rect(txt)
        txt_rect.topleft = vec2(0, 0)
        if not padding: return txt_rect
        if len(padding) == 1:  # all
            txt_rect.w += padding[0]*2
            txt_rect.h += padding[0]*2
            txt_rect.x += padding[0]
            txt_rect.y += padding[0]
        elif len(padding) == 2:  # top/bottom, left/right
            txt_rect.w += padding[1]*2
            txt_rect.h += padding[0]*2
            txt_rect.x += padding[1]
            txt_rect.y += padding[0]
        elif len(padding) == 4: # top right bottom left
            txt_rect.w += padding[1] + padding[3]
            txt_rect.h += padding[0] + padding[2]
            txt_rect.x += padding[3]
            txt_rect.y += padding[0]
        else:
            raise Exception("You Suck")   
        
        return txt_rect
    
    # def force_size(self, w, h, keep_padding=False):
    #     pass
    
    def num_lines(self, txt):
        return len(txt.split('\n'))
    
    
    def word_wrap(self, surf, x_start=0, y_start=0, max_w=False):
        if not max_w: return
        txt = self.txt.replace('\n', ' \n ')
        words = re.split(' +', txt)
        # words = [w for w in self.txt.split(' ')]
        # width, height = surf.get_size()
        line_spacing = self.font.get_sized_height() + 2
        x, y = x_start, y_start
        space = self.font.get_rect(' ')
        for word in words:
            bounds = self.font.get_rect(word)
            if x + bounds.width + bounds.x >= max_w:
                x, y = 0, y + line_spacing
            # if x + bounds.width + bounds.x >= max_w:
            #     print('oop')
            # if y + bounds.height - bounds.y >= height:
            #     print('oop')
            self.font.render_to(surf, (x, y), word, self.txt_colour)
            x += bounds.width + space.width
        return x, y

class Button(pygame.sprite.Sprite):
    def __init__(self, image, on_click: callable,  x=0, y=0, hover_image=None, click_image: TextBox=None, group=None, click_cldwn=0.3):
        if isinstance(group, pygame.sprite.Group):
            pygame.sprite.Sprite.__init__(self, group)
        else:
            pygame.sprite.Sprite.__init__(self)
            
        self.base_image = image
        self.on_click = on_click
        self.hover_image = hover_image
        self.click_image = click_image
        self.click_cldwn = click_cldwn
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.clicked = False
        self.hovered = False
        self.on_click_args = ()
        
        self.offset = vec2(0, 0)
        
    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y
    
    def reset(self):
        self.image = self.base_image
        self.clicked = False
        
    def hover(self):
        if self.hover_image:
            self.image = self.hover_image
    
    def set_click_args(self, *args):
        self.on_click_args = args
    
    def clear_click_args(self):
        self.on_click_args = ()
        
    def click(self):
        self.clicked = True
        if self.click_image:
            self.image = self.click_image
        self.on_click(*self.on_click_args)
        t = Timer(self.click_cldwn, self.reset)
        t.start()
        
    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.hovered = True
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                self.click()
        else:
            self.hovered = False
        
        if not self.clicked and self.hovered:
            self.hover()
        elif not self.clicked:
            self.reset()
            
class ToggleSwitch(pygame.sprite.Sprite):
    def __init__(self, w, h, x=0, y=0, knob_colour=pygame.Color('white'), bg_colour_on=pygame.Color('blue'), bg_colour_off=pygame.Color('black'), group=None):
        if isinstance(group, pygame.sprite.Group):
            pygame.sprite.Sprite.__init__(self, group)
        else:
            pygame.sprite.Sprite.__init__(self)
            
        self.image = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.image.get_rect()
        self.x = self.rect.x = x
        self.y = self.rect.y = y
        self.w = w
        self.h = h
        
        self.knob_colour = knob_colour
        self.bg_colour_on = bg_colour_on
        self.bg_colour_off = bg_colour_off
        
        self.value = True  # on = True, off = False
        
        self.clicked = False
        self.update_switch()
        
        self.offset = vec2(0, 0)
    
    def toggle(self):
        self.value = not self.value
        self.update_switch()
        
    def update_switch(self):
        bg_colour = self.bg_colour_on if self.value else self.bg_colour_off
        r = self.h/2
        knob_r = round(r*0.7)
        
        pygame.draw.rect(self.image, bg_colour, pygame.Rect(0, 0, self.w, self.h), border_radius=int(r))
        knob_pos = (self.w-r, r) if self.value else (r, r)
        pygame.draw.circle(self.image, self.knob_colour, knob_pos, knob_r)
        
    def move_to(self, x, y):
        self.x = self.rect.x = x
        self.y = self.rect.y = y
    
    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                self.toggle()
            elif not pygame.mouse.get_pressed()[0]:
                self.clicked = False

class ComponentDiv:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.components = []
            
        
    def add_components(self, *components):
        for c in components:
            self.components.append(c)
            c.offset = vec2(self.x, self.y)
    
    def move_to(self, x, y):
        self.x = x
        self.y = y
        for c in self.components:
            c.offset = vec2(x, y)

class ComponentGroup(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.surf = pygame.display.get_surface()
        
    def update(self):
        super().update()
        
    def draw_sprites(self):
        for sprite in self.sprites():
            self.surf.blit(sprite.image, sprite.rect.topleft + sprite.offset)