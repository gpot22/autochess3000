import math

class Car:
    def __init__(self, x, y, theta, magnet_offset):
        self.x = x
        self.y = y
        self.theta = theta
        
        self.start_time = 0
        self.end_time = 0
        
        self.target_theta = 0
        self.turn_dir = 1
    
        self.tracked_dist = 0
        self.target_dist = 0
        self.moving_dir = 1
        
        self.magnet_offset = magnet_offset
        
        magnet_pos = (x + magnet_offset[0], y + magnet_offset[1])
        self.magnet_vec_default = (self.magnet_draw_pos[0]-self.DIAMETER/2, self.magnet_draw_pos[1]-self.DIAMETER/2)
        # self.magnet_vec_rotated = None
        # self.magnet_toggled = False
        
        self._draw()
        
        # self.instructions = "turn-90,fwd30,turn30,fwd70"
        self.instructions = ""
    
    def move_to(self, x, y):
        self.x = x
        self.y = y
        
    def move_magnet_to(self, x, y):
        pass