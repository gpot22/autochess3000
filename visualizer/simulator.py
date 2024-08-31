import pygame
import pygame.gfxdraw
pygame.init()
vec2 = pygame.math.Vector2

import sys
import time
import math
import numpy as np

from chessboard import Grid
from pieces import Piece, PieceGroup
from styles import Styles
from cursor import cursor_state
from components import TextBox

from pathfinder import Pathfinder, Node_Grid, Network, update_neighbours
# from .components import TextBox, Button, ComponentGroup, ToggleSwitch

def time_in_secs():
    return time.perf_counter_ns()/1_000_000_000.0

class Simulator:
    SCR_W, SCR_H  = 600, 600
    FPS = 60
    TILE_W = 50

    def __init__(self, stockfish):
        self.stockfish = stockfish
        
        self.scr = pygame.display.set_mode((self.SCR_W, self.SCR_H))
        self.clock = pygame.time.Clock()
        
        self.piece_group = PieceGroup()

        self.grid_offset = vec2((self.SCR_W - self.TILE_W*8)/2, (self.SCR_H - self.TILE_W*8)/2)
        
    def draw_grid(self, grid):
        self.scr.blit(grid.surf, self.grid_offset)
    
    def load_game(self, board, grid):
        for i, row in enumerate(board):
            for j, piece_id in enumerate(row):
                if not piece_id.strip(): continue
                p = Piece(self.piece_group, piece_id, grid)
                p.move_to_tile(i, j, init=True)
                
    def run(self, board):
        grid = Grid(self.TILE_W, self.grid_offset, self.stockfish)
        
        piece_outline0 = PieceOutline(125, 125, pygame.Color('orange'))
        piece_outline1 = PieceOutline(450, 450, pygame.Color('cyan'))
        car0 = Car(155, 125, 0, (-30, 0), piece_outline0)
        car1 = Car(420, 450, 180, (-30, 0), piece_outline1)
        
        node_grid_outer = Node_Grid(25, 125, 8, 12, 50, pygame.Color('black'))
        node_grid_inner = Node_Grid(50, 150, 7, 11, 50, pygame.Color('blue'))
        nodes = node_grid_outer.nodes + node_grid_inner.nodes
        network = Network(0, 0, nodes, lambda: update_neighbours(node_grid_outer, node_grid_inner), car0.vel, car0.ang_vel)
        pathfinder0 = Pathfinder(network)
        
        node_grid_outer1 = Node_Grid(25, 125, 8, 12, 50, pygame.Color('black'))
        node_grid_inner1 = Node_Grid(50, 150, 7, 11, 50, pygame.Color('blue'))
        nodes1 = node_grid_outer1.nodes + node_grid_inner1.nodes
        network1 = Network(0, 0, nodes1, lambda: update_neighbours(node_grid_outer1, node_grid_inner1), car1.vel, car1.ang_vel)
        pathfinder1 = Pathfinder(network1)
        
        
        # tb = TextBox(car0.instructions, Styles.FONT1, x='center', y=20, origin='center', padding=[2], txt_colour=pygame.Color('black'))
        # self.load_game(board, grid)
        dot_grids = False
        run = True
        
        layer = 0
        pathfinders = [pathfinder0, pathfinder1]
        cars = [car0, car1]
        
        temp_start_time = 0
        while run:
            self.scr.fill(pygame.Color('white')) # BG
            events = pygame.event.get()
            for ev in events:
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        for p in self.piece_group.sprites():
                            p.selected = False
                    if ev.button == 3:
                        dot_grids = not dot_grids
                
                if ev.type == pygame.MOUSEMOTION:
                    if grid.rect.collidepoint(pygame.mouse.get_pos()):
                        cursor_state['on_board'] = True
                    else:
                        cursor_state['on_board'] = False

                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        pathfinders[layer].car = cars[layer]
                    if ev.key == pygame.K_r:
                        cars[layer].start_turn(90)
                    if ev.key == pygame.K_w:
                        cars[layer].start_fwd(120)
                    if ev.key == pygame.K_s:
                        cars[layer].start_bkwd(50)
                    if ev.key == pygame.K_m:
                        if cars[layer].magnet_toggled:
                            cars[layer].magnet_off()
                        else:
                            cars[layer].magnet_on()
                    if ev.key == pygame.K_h:
                        pathfinders[layer].get_nodes_in_radius(200, 200, 100)
                    if ev.key == pygame.K_9:
                        layer = 0
                    if ev.key == pygame.K_0:
                        layer = 1
                    # if ev.key == pygame.K_SPACE:
                    #     cars[layer].ready = True
                    # if ev.key == pygame.K_SPACE:
                    #     if pathfinder.start_node is not None and pathfinder.end_node is not None:
                    #         cars[layer].ready = True
                    #         cars[layer].instructions = pathfinder.path_instruction
            
            self.draw_grid(grid)
            grid.update(events)
            self.piece_group.update(events)
            self.piece_group.draw_sprites()
            
            car0.update(events)
            self.scr.blit(car0.image, car0.rect)
            car1.update(events)
            self.scr.blit(car1.image, car1.rect)
            
            piece_outline0.update()
            self.scr.blit(piece_outline0.image, piece_outline0.rect)
            piece_outline1.update()
            self.scr.blit(piece_outline1.image, piece_outline1.rect)
            
            # self.scr.blit(tb.image, tb.rect.topleft)
            
            if dot_grids:
                for row in grid.tiles:
                    for tile in row:
                        pygame.draw.aacircle(self.scr, 'red', (tile.global_rect.centerx, tile.global_rect.centery), 1)
            for the_car in cars:
                if the_car.turning:
                    the_car.turn()
                elif the_car.moving:
                    if the_car.moving_dir > 0:
                        the_car.fwd()
                    else:
                        the_car.bkwd()
            # if car0.turning:
            #     car0.turn()
            # elif car0.moving:
            #     if car0.moving_dir > 0:
            #         car0.fwd()
            #     else:
            #         car0.bkwd()
                
            pathfinders[layer].tick(self.scr, bg='transparent', events=events)
            
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        if pathfinders[layer].start_node is not None and pathfinders[layer].end_node is not None:
                            cars[layer].ready = True
                            print(pathfinders[layer].path_instruction)
                            cars[layer].instructions = pathfinders[layer].path_instruction
                            temp_start_time = time.perf_counter_ns()
            
            # t_elapsed = (time.perf_counter_ns()-temp_start_time)/(10**9)
            # if temp_start_time != 0:
            #     for row in pathfinder0.network.nodes:
            #         for node in row:
            #             if node.is_available_at_time(t_elapsed):
            #                 node.val = ' '
            #             else:
            #                 node.val = 'T'
            
            pygame.display.update()
            self.clock.tick(self.FPS)
            

class BoundaryRect(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface((w, h), pygame.SCRALPHA, 32).convert_alpha
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
class Car (pygame.sprite.Sprite):
    DIAMETER = 100 # mm
    RPM = 123  # rotations per minute
    WHEEL_DIAMETER = 21 # mm / rotation
    def __init__(self, x, y, theta, magnet_offset, piece_outline):
        pygame.sprite.Sprite.__init__(self)
        
        self.theta = theta
        
        self.image = pygame.Surface((self.DIAMETER, self.DIAMETER), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.x = x
        self.y = y
        
        self.dragging = False
        self.vel = self.RPM * self.WHEEL_DIAMETER/60 # mm/s
        
        self.ang_vel = self.vel/(self.DIAMETER/2) * 180/math.pi  # deg/s
        
        self.turning = False
        self.moving = False
        self.ready = False
        
        self.start_time = 0
        self.end_time = 0
        
        self.target_theta = 0
        self.turn_dir = 1
    
        self.tracked_dist = 0
        self.target_dist = 0
        self.moving_dir = 1
        
        self.magnet_offset = magnet_offset
        self.magnet_draw_pos = (self.DIAMETER/2 + magnet_offset[0], self.DIAMETER/2 + magnet_offset[1])
        
        self.magnet_vec_default = vec2(self.magnet_draw_pos[0]-self.DIAMETER/2, self.magnet_draw_pos[1]-self.DIAMETER/2)
        self.magnet_vec_rotated = None
        self.magnet_toggled = False
        
        self._draw()
        
        # self.instructions = "turn-90,fwd30,turn30,fwd70"
        self.instructions = ""
        
        self.piece_outline = piece_outline
        
    def _draw(self):
        self.image.fill('white')
        self.image.set_colorkey('white')
        radius = int((self.DIAMETER)/2)
        # body
        pygame.draw.aacircle(self.image, pygame.Color('gray60'), (radius, radius), radius-1)
        # fwd direction indicator
        pygame.draw.rect(self.image, pygame.Color('green2'), pygame.Rect(80, 47, 16, 6))
        # center location
        pygame.draw.aacircle(self.image, pygame.Color('black'), (radius, radius), 1)
        # vector twds magnet
        # pygame.draw.line(self.image, pygame.Color('red'), (radius, radius), (radius+self.magnet_vec_default.x, radius+self.magnet_vec_default.y))
        
        # magnet location
        c = pygame.Color('forestgreen') if self.magnet_toggled else pygame.Color('red')
        pygame.draw.aacircle(self.image, c, self.magnet_draw_pos , 3)
        # # piece size
        # pygame.draw.aacircle(self.image, pygame.Color('orange'), self.magnet_pos, 16, 1)
        # rotate
        self.rotate_around_center(self.theta)
        # calculated vector
        v = self.magnet_vec_rotated = self.rotate_vector(self.magnet_vec_default, self.theta*math.pi/180)
        pygame.draw.line(self.image, pygame.Color('cyan'), (radius, radius), (radius+v.x, radius+v.y))
        
        # add border after rotating so it isnt blurry af
        pygame.draw.aacircle(self.image, pygame.Color('black'), (radius, radius), radius-1, 1)
        
    def rotate_around_center(self, angle):
        # pos = (self.rect.centerx, self.rect.centery)
        
        radius = int((self.DIAMETER)/2)
        pos = (radius, radius)
        # print((self.rect.x, self.rect.y))
        # offset from pivot to center
        image_rect = self.image.get_rect(topleft = (0, 0))
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
        # print(offset_center_to_pivot)
        # roatated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        # roatetd image center
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

        # get a rotated image
        rotated_image = pygame.transform.rotate(self.image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

        # rotate and blit the image
        self.image.blit(rotated_image, rotated_image_rect)
    
        # # draw rectangle around the image
        # pygame.draw.rect(self.image, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)
    
    def rotate_vector(self, vec, theta):
        pygame_basis = np.matrix([
            [1, 0],
            [0, -1]
        ])
        rotation_matrix = np.matrix([
            [math.cos(theta), -math.sin(theta)],
            [math.sin(theta), math.cos(theta)]
        ])
        projected_rotation_matrix = pygame_basis @ rotation_matrix @ pygame_basis  # project from and to the language of pygame's coordinate system (where y-axis is flipped)
        if isinstance(vec, vec2):
            vec = np.matrix([
                [vec.x],
                [vec.y]
            ])
        rotated_vec = projected_rotation_matrix @ vec
        return vec2(rotated_vec[0, 0], rotated_vec[1, 0])
    
    def start_turn(self, theta):
        if self.turning: return print('aaaaaaa')
        if self.moving: return print('bbbbbbb')
        self.target_theta = self.theta + theta
        self.turn_dir = theta/abs(theta)
        self.turning = True
        self.start_time = time_in_secs()
    
    def end_turn(self):
        # print('hi')
        self.start_fwd(-self.magnet_offset[0])
        
    def turn(self):
        if (self.theta < self.target_theta and self.turn_dir == 1) or (self.theta > self.target_theta and self.turn_dir == -1):
            # for ev in pygame.event.get():
            #     if ev.type == pygame.QUIT:
            #         pygame.quit()
            #         sys.exit()
            # self._draw()
            # pygame.display.get_surface().blit(self.image, self.rect)
            # pygame.display.update()
            
            self.end_time = time_in_secs()
            dt = self.end_time - self.start_time
            self.theta += self.ang_vel*dt*self.turn_dir
            self.start_time = time_in_secs()
            return
        self.theta = self.target_theta
        self.theta %= 360
        self.turning = False
        self.end_turn()
        # self._draw()
        # pygame.display.get_surface().blit(self.image, self.rect)
        # pygame.display.update()

    def start_fwd(self, dist):
        if self.turning: return print('aaaaaaa')
        if self.moving: return print('bbbbbbb')
        self.moving = True
        self.moving_dir = 1
        self.tracked_dist = 0
        self.target_dist = dist
        self.target_pos = (self.x + dist * math.cos(self.theta*math.pi/180), self.y + dist * -math.sin(self.theta*math.pi/180))
        self.start_time = time_in_secs()
    
    def fwd(self):
        if self.tracked_dist < self.target_dist:
            self.end_time = time_in_secs()
            dt = self.end_time - self.start_time
            self.tracked_dist += self.vel*dt
            self.x += self.vel * math.cos(self.theta*math.pi/180) * dt
            self.y += self.vel * -math.sin(self.theta*math.pi/180) * dt
            self.start_time = time_in_secs()
            return
        self.x = self.target_pos[0]
        self.y = self.target_pos[1]
        self.moving = False
    
    def start_bkwd(self, dist):
        if self.turning: return print('aaaaaaa')
        if self.moving: return print('bbbbbbb')
        self.moving = True
        self.moving_dir = -1
        self.tracked_dist = 0
        self.target_dist = dist
        self.target_pos = (self.x - dist * math.cos(self.theta*math.pi/180), self.y - dist * -math.sin(self.theta*math.pi/180))
        self.start_time = time_in_secs()
    
    def bkwd(self):
        if self.tracked_dist < self.target_dist:
            self.end_time = time_in_secs()
            dt = self.end_time - self.start_time
            self.tracked_dist += self.vel*dt
            self.x -= self.vel * math.cos(self.theta*math.pi/180) * dt
            self.y -= self.vel * -math.sin(self.theta*math.pi/180) * dt
            self.start_time = time_in_secs()
            return
        self.x = self.target_pos[0]
        self.y = self.target_pos[1]
        self.moving = False
    
    def is_busy(self):
        return self.turning or self.moving
    
    def get_magnet_pos(self):
        return self.x+self.magnet_offset[0], self.y+self.magnet_offset[1]
    
    def execute_instruction(self, instruction):
        if instruction.startswith('turn'):
            val = float(instruction[4:])
            
            self.start_turn(val)
        elif instruction.startswith('fwd'):
            val = float(instruction[3:])
            if val < 0:
                self.start_bkwd(-val)
            else:
                self.start_fwd(val)
        elif instruction.startswith('bkwd'):
            val = float(instruction[4:])
            self.start_bkwd(val)
        elif instruction.startswith('mag'):
            val = int(instruction[3:])
            print(val)
            if val == 2:
                if self.magnet_toggled:
                    self.magnet_off()
                    print('toggled off')
                else:
                    self.magnet_on()
                    print('toggled on')
            elif val == 1:
                self.magnet_on()
                # print('on')
            else:
                self.magnet_off()
                # print('off')
            # time.sleep(0.5)
        # elif instruction == 'mag_on':
        #     self.magnet_on()
        #     time.sleep(0.5)
        # elif instruction == 'mag_off':
        #     self.magnet_off()
        #     time.sleep(0.5)
            
    def update(self, events):
        pos = pygame.mouse.get_pos()
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if self.rect.collidepoint(pos):
                    self.dragging = True
                    
            if ev.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.rect.center = pos
                    
            
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if self.dragging:
                    self.dragging = False
        if self.instructions and not self.is_busy() and self.ready:
            if not ',' in self.instructions:
                instruction = self.instructions
                self.instructions = ''
            else:
                idx = self.instructions.index(',')
                instruction = self.instructions[0:idx]
                self.instructions = self.instructions[idx+1:]
            self.execute_instruction(instruction)

        self._draw()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def magnet_on(self):
        self.piece_outline.stick_to_car(self)
        self.magnet_toggled = True
        
    def magnet_off(self):
        self.piece_outline.remove_from_car()
        self.magnet_toggled = False
        
class PieceOutline(pygame.sprite.Sprite):
    DIAMETER = 32
    def __init__(self, x, y, colour):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface((self.DIAMETER, self.DIAMETER), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.x = x
        self.y = y
        self.colour = colour
        self.car = None
        
        self._draw()
        
    def _draw(self):
        radius = self.DIAMETER/2
        pygame.draw.aacircle(self.image, self.colour, (radius, radius), radius, 2)
        
    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.rect.center = (x, y)
    
    def stick_to_car(self, car):
        self.car = car
        
    def remove_from_car(self):
        self.car = None
    
    def follow_car(self):
        if self.car is None: return
        self.move_to(self.car.x + self.car.magnet_vec_rotated.x, self.car.y+self.car.magnet_vec_rotated.y)
    
    def update(self):
        self.follow_car()