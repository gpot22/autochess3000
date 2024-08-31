import pygame
pygame.init()
vec2 = pygame.math.Vector2

import sys
import math
from queue import PriorityQueue
import chessboard

BARRIER = '#'
START = 'i'
END = 'x'
PATH = 'o'
OPEN = '+'
CLOSED = '-'
EMPTY = ' '
TEST = 'T'

legend = {
    BARRIER: pygame.Color('black'),
    START: pygame.Color('cyan'),
    END: pygame.Color('orange'),
    PATH: pygame.Color('purple'),
    OPEN: pygame.Color('green'),
    CLOSED: pygame.Color('red'),
    EMPTY: pygame.Color('white'),
    TEST: pygame.Color('yellow')
}

class Pathfinder:
    def __init__(self, network):
        self.network = network
        self.start_node = None
        self.end_node = None
        
        self.started = False
        self.current_char = BARRIER
        
        self.path_nodes = []
        self.path_instruction = ""
    
    def astar(self):
        if self.start_node is None or self.end_node is None: return print('rah')
        
        count = 0
        open_set = PriorityQueue()          # (f_val, count, node)
        open_set.put((0, 0, count, self.start_node))
        came_from = {}
        nodes = self.network.nodes
        
        f_score = {node: float('inf') for row in nodes for node in row}
        g_score = {node: float('inf') for row in nodes for node in row}
        time_cost_so_far = {node: float('inf') for row in nodes for node in row}
        
        # f = g + h; g = 0 so f = h for now
        f_score[self.start_node] = self.h_score(self.start_node.get_pos(), self.end_node.get_pos())
        g_score[self.start_node] = 0
        
        open_set_hash = {self.start_node}
        
        while not open_set.empty():
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            current_node = open_set.get()[-1]
            open_set_hash.remove(current_node)
            
            if current_node == self.end_node:
                self.reconstruct_path(came_from, current_node)
                self.start_node.val = START
                self.end_node.val = END
                return True
            
            for neighbour in current_node.neighbours:
                temp_g_score = g_score[current_node] + 1  # WEIGHT
                new_time_cost = time_cost_so_far[current_node] + self.network.time_elapsed_move(current_node, neighbour)
                if current_node in came_from:
                    prev_node = came_from[current_node]
                    new_time_cost += self.network.time_elapsed_turn(prev_node, current_node, neighbour)
                if temp_g_score < g_score[neighbour]:
                    came_from[neighbour] = current_node
                    g_score[neighbour] = temp_g_score
                    f_score[neighbour] = temp_g_score + self.h_score(neighbour.get_pos(), self.end_node.get_pos())
                    
                    time_cost_so_far[neighbour] = new_time_cost
                    if neighbour not in open_set_hash:
                        if neighbour.is_available_at_time(new_time_cost):
                            count += 1
                            open_set.put((f_score[neighbour], time_cost_so_far[neighbour], count, neighbour))
                            open_set_hash.add(neighbour)
                            neighbour.val = OPEN
            self.draw_network()
            if current_node != self.start_node:
                neighbour.val = CLOSED
        print('bap')
        return False
    
    def h_score(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        
        c = math.sqrt((x2-x1)**2 + (y2-y1)**2)  # distance via pythag
        m = abs(x1-x2) + abs(y1-y2)             # distance via manhattan
        return m
    
    def reconstruct_path(self, came_from, current):
        # current_theta = 0
        nodes = [current]
        while current in came_from:
            current = came_from[current]
            nodes.append(current)
            current.val = PATH
            self.draw_network()
        # nodes.append(self.start_node)
        nodes.reverse()
        self.path_nodes = nodes
        
    def draw_network(self):
        self.network.draw()
        
    def update_network(self, events):
        for row in self.network.nodes:
            for node in row:
                node.update(events)
    
    # def draw_network_nodes(self):
    #     pass
    
    # def draw_network_edges(self):
    #     pass
    
    def get_hovered_node(self):
        for row in self.network.nodes:
            for node in row:
                if node.hover: return node
        return False
    
    def get_nodes_in_radius(self, x, y, r):
        nodes = []
        for row in self.network.nodes:
            for node in row:
                node_x, node_y = node.get_pos()
                if math.sqrt((node_x-x)**2 + (node_y-y)**2) < r:
                    nodes.append(node)
                    node.val = TEST
        return nodes
    
    def path_to_instruction(self, start_theta=0):
        if not self.path_nodes: return
        current_theta = start_theta
        # prev_node = self.path_nodes[0]
        # next_node = self.path_nodes[1]
        dtheta = 0
        fwd_dist = 0
        for i in range(1, len(self.path_nodes)):
            prev_node = self.path_nodes[i-1]
            next_node = self.path_nodes[i]
            # self.get_nodes_in_radius(next_node.x, next_node.y, 200)
            # print((prev_node.x, prev_node.y), (next_node.x, next_node.y))
            dx = next_node.x - prev_node.x
            dy = next_node.y - prev_node.y
            dist = math.sqrt(dx**2 + dy**2)
            if dx == 0:
                if dy < 0:
                    theta = 90
                else:
                    theta = 270
            elif dy == 0:
                if dx > 0:
                    theta = 0
                else:
                    theta = 180
            else:
                theta = math.atan(abs(dy/dx)) * 180/math.pi
                if dy < 0 and dx < 0:
                    theta += 90
                elif dy > 0 and dx < 0:
                    theta += 180
                elif dy > 0 and dx > 0:
                    theta += 270
            
            # if current_theta != theta:
            dtheta = theta - current_theta
            current_theta = theta
            if dtheta != 0:
                if fwd_dist != 0:
                    self.path_instruction += f'fwd{fwd_dist},'
                    fwd_dist = 0
                self.path_instruction += 'mag0,'
                self.path_instruction += 'fwd-30,'
                self.path_instruction += f'turn{dtheta},'
                self.path_instruction += 'mag1,'
                # if fwd_dist != 0:
                #     # if fwd_dist > 30:
                #     #     self.path_instruction += f'fwd30,'
                #     #     self.path_instruction += 'mag1,'
                #     #     fwd_dist-=30
                #     if fwd_dist == -30:
                #         self.path_instruction += 'mag0,'
                #         self.path_instruction += f'fwd{fwd_dist},'
                #     elif fwd_dist>30:
                #         self.path_instruction += f'fwd{fwd_dist-30},'
                #         self.path_instruction += m
                        
                #     fwd_dist = 0
                # self.path_instruction += f'turn{dtheta},'
                # self.path_instruction += 'mag1,'
                # fwd_dist-=30
                
            # elif dtheta == last_dtheta == 0:
            fwd_dist += dist
            if i == len(self.path_nodes)-1 and fwd_dist>0:
                self.path_instruction += f'fwd{fwd_dist},'
        
        if self.path_instruction.endswith(','):
            self.path_instruction = self.path_instruction[:-1]
                
            # theta = 
    def update_path_times(self):
        for i in range(len(self.path_nodes)):
            prev_node = None
            current_node = self.path_nodes[i]
            next_node = None
            if i-1 > 0:
                prev_node = self.path_nodes[i-1]
                # current_node.time = prev_node.time + self.network.time_elapsed_move()
            if i+1 < len(self.path_nodes):
                next_node = self.path_nodes[i+1]
            
            if next_node is not None:
                current_node.time[0] = self.network.time_elapsed_move(current_node, next_node)
                if prev_node is not None:
                    current_node.time[0] += prev_node.time[1]
                    current_node.time[1] = current_node.time[0] + self.network.time_elapsed_turn(prev_node, current_node, next_node)
                else:
                    current_node.time[1] = current_node.time[0]
            elif prev_node is not None:
                current_node.time[0] = current_node.time[1] =  prev_node.time[1]
            
    def update_node_busy_times(self):
        for node in self.path_nodes:
            nodes_in_range = self.get_nodes_in_radius(node.x, node.y, 105)
            for busy_node in nodes_in_range:
                busy_node.add_busy_interval(node.time[0], node.time[1])
            
    
    def tick(self, scr, my_board=None, bg='white', events=None):
        if events is None:
            events = pygame.event.get()
        if bg != 'transparent':
            scr.fill(bg)
        if my_board is not None:
            scr.blit(my_board.surf, my_board.offset)
            my_board.update(events)
        self.network.update_neighbours()
        
        self.update_network(events)
        self.draw_network()
        for ev in events:
            mouse_states = pygame.mouse.get_pressed()
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            node = self.get_hovered_node()
            if node and (ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEMOTION):
                if mouse_states[0]: # lmb
                    if self.current_char == START:
                        if self.start_node is not None:
                            self.start_node.val = EMPTY
                        self.start_node = node
                    elif node.val == START:
                        self.start_node = None
                    
                    if self.current_char == END:
                        if self.end_node is not None:
                            self.end_node.val = EMPTY
                        self.end_node = node
                    elif node.val == END:
                        self.start_node = None
                    
                    node.val = self.current_char
                elif mouse_states[2]:  # rmb
                    if node == START:
                        self.start_node = None
                    if node == END:
                        self.end_node = None
                    node.val = EMPTY
                self.network.update_neighbours()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:  # wall
                    self.current_char = BARRIER
                elif ev.key == pygame.K_2:  # start
                    self.current_char = START
                elif ev.key == pygame.K_3:  # end
                    self.current_char = END
                
                if ev.key == pygame.K_SPACE and not self.started:
                    self.network.update_neighbours()
                    self.started = True
                    self.astar()
                    self.path_to_instruction(self.car.theta)
                    # self.update_path_times()
                    # self.update_node_busy_times()
                    # algorithm(lambda: draw(net0, net1), net0, net1, start, end)
        
        
        
        pygame.display.update()
    
    def run(self, scr, my_board=None):
        clock = pygame.time.Clock()
        
        self.start_node = None
        self.end_node = None
        
        self.started = False
        
        self.current_char = BARRIER
        
        self.network.update_neighbours()
        
        while True:
            
            self.tick(scr, my_board)
            clock.tick(60)

class Network:
    def __init__(self, x, y, nodes, update_neighbours_alg, vel, ang_vel):
        self.x = x
        self.y = y
        self.nodes = nodes
        self.update_neighbours_alg = update_neighbours_alg
        self.vel = vel
        self.ang_vel = ang_vel
        for row in nodes:
            for node in row:
                node.x += x
                node.y += y
                
    def update_neighbours(self):
        self.update_neighbours_alg()
        
    def draw(self):
        self.draw_nodes()
        self.draw_edges()
    
    def draw_nodes(self):
        for row in self.nodes:
            for node in row:
                node.draw()
    
    def draw_edges(self):
        scr = pygame.display.get_surface()
        for row in self.nodes:
            for node in row:
                for neighbour in filter(lambda neighbour_node:node.is_toplefter(neighbour_node), node.neighbours):
                    colour = pygame.Color('black')
                    line_w = 1
                    if (node.val == PATH or node.val == START or node.val == END) and (neighbour.val == PATH or neighbour.val == START or neighbour.val == END):
                        colour = legend[PATH]
                        line_w = 3
                    pygame.draw.line(scr, colour, (node.x, node.y), (neighbour.x, neighbour.y), line_w)

    def time_elapsed_move(self, current_node, next_node):
        d = current_node.dist_to(next_node)
        return d/self.vel
    
    def time_elapsed_turn(self, prev_node, current_node, next_node):
        u = (current_node.x-prev_node.x, current_node.y-prev_node.y)
        v = (current_node.x-next_node.x, current_node.y-next_node.y)
        
        udotv = u[0]*v[0] + u[1]*v[1]
        ulen = math.sqrt(u[0]**2 + u[1]**2)
        vlen = math.sqrt(v[0]**2 + v[1]**2)
        theta = math.acos(udotv/(ulen*vlen)) * 180/math.pi
        print(theta)
        
        return theta/self.ang_vel
        
    
class Node_Grid:
    NODE_RADIUS = 7
    def __init__(self, x, y, row_count, column_count, gap_size, node_outline_colour=pygame.Color('black')):
        self.x = x
        self.y = y
        self.row_count = row_count
        self.column_count = column_count
        self.gap_size = gap_size
        self.node_outline_colour = node_outline_colour
        
        self.nodes = self._build()
        
    def _build(self):
        nodes = []
        for i in range(self.row_count):
            nodes.append([])
            for j in range(self.column_count):
                node = Node(j*self.gap_size + self.x, i*self.gap_size + self.y, self.NODE_RADIUS, self, self.node_outline_colour)
                nodes[i].append(node)
        return nodes
    
    def get_node_neighbours(self, node, row, col):
        neighbours = []
        if node.val == BARRIER:
            return []
        if row > 0 and not self.nodes[row-1][col].val == BARRIER:  #above
            neighbours.append(self.nodes[row-1][col])
        if row < self.row_count - 1 and not self.nodes[row+1][col].val == BARRIER:  #below
            neighbours.append(self.nodes[row+1][col])    
        if col > 0 and not self.nodes[row][col-1].val == BARRIER:  #left
            neighbours.append(self.nodes[row][col-1])
        if col < self.column_count - 1 and not self.nodes[row][col+1].val == BARRIER:  #right
            neighbours.append(self.nodes[row][col+1])
        return neighbours
    
    def update_grid_neighbours(self):
        for i in range(self.row_count):
            for j in range(self.column_count):
                node = self.nodes[i][j]
                node.neighbours = self.get_node_neighbours(node, i, j)
                # if node.val == BARRIER:
                #     neigh
                

class Node:
    def __init__(self, x, y, radius, node_grid: Node_Grid=None, outline_colour=pygame.Color('black')):
        self.x = x
        self.y = y
        self.radius = radius
        
        self.node_grid = node_grid
        self.val = EMPTY
        # self.colour = pygame.Color('white')
        self.outline_colour = outline_colour
        
        # self.x = self.col * self.net.gap_size + self.net.x
        # self.y = self.row * self.net.gap_size + self.net.y
        
        self.rect = pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)
        self.hover = False
        
        self.time = [0, 0]
        self.neighbours = []
        self.busy_intervals = []
        
    def get_pos(self):
        return self.x, self.y
    
    def is_toplefter(self, other):
        if self.y < other.y:
            return True
        if self.x < other.x:
            return True
        return False
    
    def dist_to(self, node):
        return math.sqrt((node.x-self.x)**2 + (node.y-self.y)**2)
    
    def is_available_at_time(self, t):
        for interval in self.busy_intervals:
            if t > interval[0] and t < interval[1]:
                return False
        return True
    
    def merge_busy_intervals(self):
        # Sort intervals based on start values
        self.busy_intervals.sort(key=lambda x: x[0])

        res = [self.busy_intervals[0]]

        for i in range(1, len(self.busy_intervals)):
            last = res[-1]
            curr = self.busy_intervals[i]

            # If current overlaps with the last
            # merged, merge them
            if curr[0] <= last[1]:
                last[1] = max(last[1], curr[1])
            else:
                # Add current to the result
                res.append(curr)
                
        self.busy_intervals = res
    
    def add_busy_interval(self, t0, t1):
        self.busy_intervals.append([t0, t1])
        self.merge_busy_intervals()
                
    def draw(self):
        scr = pygame.display.get_surface()
        pygame.draw.aacircle(scr, legend[self.val], (self.x, self.y), self.radius)
        pygame.draw.aacircle(scr, self.outline_colour, (self.x, self.y), self.radius, 1)
    
    def update(self, events):
        self.hover = False
        for ev in events:
            mouse_pos = pygame.mouse.get_pos()
            if(ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEMOTION) and self.rect.collidepoint(mouse_pos):
                self.hover = True
                

def update_neighbours(grid_outer, grid_inner):
    for i, row in enumerate(grid_outer.nodes):
        for j, node in enumerate(row):
            if node.val == BARRIER: 
                continue
            node.neighbours = grid_outer.get_node_neighbours(node, i, j)
    
    for i, row in enumerate(grid_inner.nodes):
        for j, node in enumerate(row):
            if node.val == BARRIER: 
                continue
            node.neighbours = grid_inner.get_node_neighbours(node, i, j)
            # cross neighbours
            for m in range(2):
                for n in range(2):
                    if grid_outer.nodes[i+m][j+n].val != BARRIER:
                        node.neighbours.append(grid_outer.nodes[i+m][j+n])
                        grid_outer.nodes[i+m][j+n].neighbours.append(node)

def main():
    scr_w, scr_h = 600, 600
    scr = pygame.display.set_mode((scr_w, scr_h))
    node_grid_outer = Node_Grid(100, 100, 9, 9, 50, pygame.Color('black'))
    node_grid_inner = Node_Grid(125, 125, 8, 8, 50, pygame.Color('blue'))
    nodes = node_grid_outer.nodes + node_grid_inner.nodes
    network = Network(0, 0, nodes, lambda: update_neighbours(node_grid_outer, node_grid_inner), 50, pygame.Color('black'))
    pathfinder = Pathfinder(network)
    my_board = chessboard.Grid(50, vec2(100, 100), None)
    pathfinder.run(scr, my_board=my_board)

if __name__ == '__main__':
    main()