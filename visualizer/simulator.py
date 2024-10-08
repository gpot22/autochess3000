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
        car0 = Car(100, 100, 0, (-30, 0), piece_outline0)
        car1 = Car(500, 100, 180, (-30, 0), piece_outline1)
        
        node_grid_outer = Node_Grid(25, 125, 8, 12, 50, pygame.Color('black'))
        node_grid_inner = Node_Grid(50, 150, 7, 11, 50, pygame.Color('blue'))
        nodes = node_grid_outer.nodes + node_grid_inner.nodes
        network0 = Network(0, 0, nodes, lambda: update_neighbours(node_grid_outer, node_grid_inner), car0.vel, car0.ang_vel)
        pathfinder0 = Pathfinder(network0)
        
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
                elif the_car.waiting:
                    the_car.wait()
            # if car0.turning:
            #     car0.turn()
            # elif car0.moving:
            #     if car0.moving_dir > 0:
            #         car0.fwd()
            #     else:
            #         car0.bkwd()
                
            pathfinders[layer].display_tick(self.scr, bg='transparent', events=events)
            
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        if pathfinders[layer].start_node is not None and pathfinders[layer].end_node is not None:
                            self.captured_piece_pathfind(pathfinders, cars, layer) 
                            # cars[layer].ready = True
                            # print(pathfinders[layer].path_instruction)
                            # cars[layer].instructions = pathfinders[layer].path_instruction
                            
            
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
            
    def captured_piece_pathfind(self, pathfinders, cars, layer):
        other_layer = int(not layer)
        
        
        # drawn start node = attacking piece
        # drawn end node = captured piece
        attacking_piece_pathfinder = pathfinders[layer]
        captured_piece_pathfinder = pathfinders[other_layer]
        
        # location of captured piece
        x0 = attacking_piece_pathfinder.end_node.x
        y0 = attacking_piece_pathfinder.end_node.y
        # dist_to_car0 = math.sqrt((cars[0].x-x0)**2 + (cars[0].y-y0)**2)
        # dist_to_car1 = math.sqrt((cars[1].x-x0)**2 + (cars[1].y-y0)**2)
        
        dist_to_car0 = abs(cars[0].x-x0)
        dist_to_car1 = abs(cars[1].x-x0)
        if dist_to_car0 < dist_to_car1:
            attacking_piece_car = cars[1]
            captured_piece_car = cars[0]
        else:
            attacking_piece_car = cars[0]
            captured_piece_car = cars[1]
            
        if captured_piece_pathfinder.start_node is not None:
            captured_piece_pathfinder.start_node.val = ' '
        if captured_piece_pathfinder.end_node is not None:
            captured_piece_pathfinder.end_node.val = ' '
        
        captured_piece_pathfinder.start_node = captured_piece_pathfinder.network.get_node_at_pos(
            attacking_piece_pathfinder.end_node.x, attacking_piece_pathfinder.end_node.y)
        
        captured_piece_pathfinder.end_node = captured_piece_pathfinder.network.get_node_at_square('i2')
        
        attacking_piece_pathfinder.find_path()
        captured_piece_pathfinder.find_path()
        
        atk_start, atk_end = attacking_piece_pathfinder.path_to_instruction(attacking_piece_car)
        capt_start, capt_end = captured_piece_pathfinder.path_to_instruction(captured_piece_car)
        
        attacking_piece_car.ready = True
        attacking_piece_car.instructions = attacking_piece_pathfinder.path_instruction
        attacking_piece_car.update_time_data()
        # print(attacking_piece_car.instructions)
        print(attacking_piece_car.time_data)
        captured_piece_car.ready = True
        captured_piece_car.instructions = captured_piece_pathfinder.path_instruction
        captured_piece_car.update_time_data()
        # print(captured_piece_car.instructions)
        
        
        
        done = False
        time_step = 0.1
        
        total_time_elapsed = min(attacking_piece_car.time_data[-1], captured_piece_car.time_data[-1])
        
        while not done:
            
            print('aa')
            done = True
            attempts = 0
            time_elapsed = 0
            wait_time = 0
            saved_attacking_piece_car_instructions = attacking_piece_car.instructions
            
            while time_elapsed < total_time_elapsed:
                x0, y0 = attacking_piece_car.get_pos_at_time(time_elapsed)
                x1, y1 = captured_piece_car.get_pos_at_time(time_elapsed)
                dist = ((x1-x0)**2+(y1-y0)**2)**0.5
                car_diameter = 100
                if dist < car_diameter + 50:  # collision!!!
                    wait_time += 0.1
                    # print('idx, move, val')
                    # print(f't{time_elapsed}:', attacking_piece_car.get_index_of_instruction_at_time(time_elapsed))
                elif wait_time > 0:
                    
                    idx = attacking_piece_car.get_index_of_instruction_at_time(time_elapsed-wait_time)
                    while idx >= 0:
                        instruction_list = attacking_piece_car.instructions.split(',')
                        instruction_list.insert(idx, f'wait{wait_time}')
                    # while idx >= 0:
                        
                    #     instruction_list = attacking_piece_car.instructions.split(',')
                    #     if instruction_list[idx].startswith('go') and (idx==0 or not instruction_list[idx-1].startswith('wait')):
                    #         instruction_list.insert(idx, f'wait{wait_time}')
                    #         attacking_piece_car.instructions = ','.join(instruction_list)
                    #         attacking_piece_car.time_data.insert(idx+1, ('wait', wait_time, wait_time))
                    #         total_time_elapsed += wait_time
                    #         wait_time = 0
                    #         saved_wait_time = wait_time
                            
                    #         break
                    #     elif instruction_list[idx-1].startswith('wait'):
                    #         val = instruction_list[idx-1][4:]
                    #         if val == '0':
                    #             continue
                    #         instruction_list[idx-1] = 'wait0'
                    #         idx-=1
                    #     else:
                    #         print('yeet')
                    #         idx-=1
                    # else:
                    #     instruction_list.insert(0, f'wait{saved_wait_time}')
                    #     time_elapsed += saved_wait_time
                    #     print("AAAAAAAAAAAAAAAAAAAAAAAAAAAG")
                    # done = False
                    # wait_period_count+=1
                attempts += 1
                time_elapsed += time_step
            if wait_time > 0:
                print('WAIT TIME IS ZERO WHEN IT SHOULDNT BE :)')
        print(attacking_piece_car.instructions)
        
class BoundaryRect(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface((w, h), pygame.SCRALPHA, 32).convert_alpha
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
class Car(pygame.sprite.Sprite):
    DIAMETER = 100 # mm
    RPM = 123  # rotations per minute
    WHEEL_DIAMETER = 21 # mm / rotation
    def __init__(self, x, y, theta, magnet_offset, piece_outline):
        pygame.sprite.Sprite.__init__(self)
        
        self.theta = theta
        self.rest_theta = theta
        
        self.image = pygame.Surface((self.DIAMETER, self.DIAMETER), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.x = x
        self.y = y
        
        self.dragging = False
        self.vel = self.RPM * self.WHEEL_DIAMETER/60 # mm/s
        
        self.ang_vel = self.vel/(self.DIAMETER/2) * 180/math.pi  # deg/s
        
        self.turning = False
        self.moving = False
        self.waiting = False
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
        self.time_data = []
        
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
        if self.waiting: return print('cccccccc')
        self.target_theta = self.theta + theta
        self.turn_dir = theta/abs(theta)
        self.turning = True
        self.start_time = time_in_secs()
    
    def end_turn(self):
        # print('hi')
        # self.start_fwd(-self.magnet_offset[0])
        pass
        
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
        
    def start_wait(self, secs):
        if self.turning: return print('aaaaaaa')
        if self.moving: return print('bbbbbbb')
        if self.waiting: return print('cccccccc')
        
        self.waiting = True
        
        # self.wait_time_elapsed = 0
        self.target_wait_time = secs
        self.start_time = time_in_secs()
        
    def wait(self):
        dt = time_in_secs() - self.start_time
        if dt < self.target_wait_time:
            print(dt)
            return
        self.waiting = False
        

    def start_fwd(self, dist):
        if self.turning: return print('aaaaaaa')
        if self.moving: return print('bbbbbbb')
        if self.waiting: return print('cccccccc')
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
        if self.waiting: return print('cccccccc')
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
        return self.turning or self.moving or self.waiting
    
    def get_magnet_pos(self):
        return self.x+self.magnet_offset[0], self.y+self.magnet_offset[1]
    
    def execute_instruction(self, instruction):
        if instruction.startswith('turn'):
            val = float(instruction[4:])
            
            self.start_turn(val)
        elif instruction.startswith('go'):
            val = float(instruction[2:])
            if val < 0:
                self.start_bkwd(-val)
            else:
                self.start_fwd(val)
        elif instruction.startswith('bkwd'):
            val = float(instruction[4:])
            self.start_bkwd(val)
        elif instruction.startswith('mag'):
            val = int(instruction[3:])
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
        elif instruction.startswith('wait'):
            val = float(instruction[4:])
            self.start_wait(val)
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
        
    def update_time_data(self):
        time_data = [('start', 0, (self.x, self.y, self.theta))]
        time_elapsed = 0
        for instruction in self.instructions.split(','):
            t = 0
            if instruction.startswith('go'):
                val = float(instruction[2:])
                time_data.append(('go', t:=abs(val)/self.vel, val))
            elif instruction.startswith('turn'):
                val = float(instruction[4:])
                time_data.append(('turn', t:=abs(val)/self.ang_vel, val))
            elif instruction.startswith('mag'):
                time_data.append(('mag', 0, 0))
            elif instruction.startswith('wait'):
                val = float(instruction[4:])
                time_data.append(('wait', t:=val, val))
            time_elapsed += t
        time_data.append(time_elapsed)
        self.time_data = time_data
        
    def get_pos_at_time(self, t): # must call update_time_data() for this method to be viable
        if not self.time_data: return print("no time_data")
        datum = self.time_data[0]
        x, y, theta = datum[2]
        time_elapsed = 0
        for i in range(1, len(self.time_data)-1):
            datum = self.time_data[i]
            if t > time_elapsed and t < time_elapsed + datum[1]:
                ratio = (t-time_elapsed)/datum[1]
                if datum[0] == 'go':
                    x += datum[2]*math.cos(theta*math.pi/180)*ratio
                    y += datum[2]*-math.sin(theta*math.pi/180)*ratio
                elif datum[0] == 'turn':
                    theta += datum[2]*ratio
                elif datum[0] == 'mag':
                    pass
                elif datum[0] == 'wait':
                    pass
                return x, y
            else:
                if datum[0] == 'go':
                    x += datum[2]*math.cos(theta*math.pi/180)
                    y += datum[2]*-math.sin(theta*math.pi/180)
                elif datum[0] == 'turn':
                    theta += datum[2]
                elif datum[0] == 'mag':
                    pass
                elif datum[0] == 'wait':
                    pass
            time_elapsed += datum[1]
        
        return x, y
        
    def get_index_of_instruction_at_time(self, t):
        time_elapsed = 0
        for i in range(1, len(self.time_data)-1):
            datum = self.time_data[i]
            if t > time_elapsed and t < time_elapsed + datum[1]:
                # return i-1, datum[0], datum[2]
                return i-1
            time_elapsed += datum[1]
    
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