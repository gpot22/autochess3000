import pygame
pygame.init()
vec2 = pygame.math.Vector2

import sys
import math
from queue import PriorityQueue
from .. import chessboard

BARRIER = '#'
START = 'i'
END = 'x'
PATH = 'o'
OPEN = '+'
CLOSED = '-'
EMPTY = ' '

legend = {
    BARRIER: pygame.Color('black'),
    START: pygame.Color('cyan'),
    END: pygame.Color('orange'),
    PATH: pygame.Color('purple'),
    OPEN: pygame.Color('green'),
    CLOSED: pygame.Color('red'),
    EMPTY: pygame.Color('white')
}

scr_w, scr_h = 800, 800
scr = pygame.display.set_mode((scr_w, scr_h))

class Network:
    NODE_RADIUS = 7
    def __init__(self, x, y, row_count, column_count, gap_size, node_outline_colour=pygame.Color('black')):
        self.x = x
        self.y = y
        self.row_count = row_count
        self.column_count = column_count
        self.width = (self.column_count-1)*gap_size
        self.height = (self.row_count-1)*gap_size
        self.gap_size = gap_size
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.line_colour = pygame.Color('grey')
        self.node_outline_colour = node_outline_colour
        
        self.nodes = self._build()
        
    def _build(self):
        nodes = []
        for i in range(self.row_count):
            nodes.append([])
            for j in range(self.column_count):
                node = Node(i, j, self.NODE_RADIUS, self, self.node_outline_colour)
                nodes[i].append(node)
        return nodes

    # def draw_gridlines(self):
    #     pygame.draw.rect(scr, self.line_colour, pygame.Rect(self.rect.x, self.rect.y, self.rect.width+1, self.rect.height+1), 1)
    #     # pygame.draw.rect(self.image, self.line_colour, pygame.Rect(0, 0, self.width, self.height), 1)
    #     for i in range(1, self.column_count-1): # vertical
    #         pygame.draw.line(scr, self.line_colour, (self.x+i*self.gap_size, self.y), (self.x+i*self.gap_size, self.y+self.height))
    #     for i in range(1, self.row_count-1): # vertical
    #         pygame.draw.line(scr, self.line_colour, (self.x, self.y+i*self.gap_size), (self.x+self.width, self.y+i*self.gap_size))

class Node:
    def __init__(self, row, col, radius, network: Network, outline_colour=pygame.Color('black')):
        self.row = row
        self.col = col
        self.radius = radius
        self.net = network
        self.val = EMPTY
        # self.colour = pygame.Color('white')
        self.outline_colour = outline_colour
        
        self.x = self.col * self.net.gap_size + self.net.x
        self.y = self.row * self.net.gap_size + self.net.y
        
        self.rect = pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)
        self.hover = False
        
        self.neighbours = []
        
    def get_pos(self):
        return self.x, self.y
    
    def draw(self):
        pygame.draw.aacircle(scr, legend[self.val], (self.x, self.y), self.radius)
        pygame.draw.aacircle(scr, self.outline_colour, (self.x, self.y), self.radius, 1)
    
    def get_neighbours(self):
        neighbours = []
        if self.val == BARRIER:
            return []
        if self.row > 0 and not self.net.nodes[self.row-1][self.col].val == BARRIER:  #above
            neighbours.append(self.net.nodes[self.row-1][self.col])
        if self.row < self.net.row_count - 1 and not self.net.nodes[self.row+1][self.col].val == BARRIER:  #below
            neighbours.append(self.net.nodes[self.row+1][self.col])    
        if self.col > 0 and not self.net.nodes[self.row][self.col-1].val == BARRIER:  #left
            neighbours.append(self.net.nodes[self.row][self.col-1])
        if self.col < self.net.column_count - 1 and not self.net.nodes[self.row][self.col+1].val == BARRIER:  #right
            neighbours.append(self.net.nodes[self.row][self.col+1])
        return neighbours
    
    def update(self, events):
        self.hover = False
        for ev in events:
            mouse_pos = pygame.mouse.get_pos()
            if(ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEMOTION) and self.rect.collidepoint(mouse_pos):
                self.hover = True
    
    # def update(self, events, current_char):
    #     for ev in events:
    #         mouse_states = pygame.mouse.get_pressed()
    #         mouse_pos = pygame.mouse.get_pos()
    #         if (ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEMOTION) and self.rect.collidepoint(mouse_pos):
    #             if mouse_states[0]:  # lmb
    #                 if current_char == START:
    #                     if start is 
    
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    
    c = math.sqrt((x2-x1)**2 + (y2-y1)**2)  # distance via pythag
    m = abs(x1-x2) + abs(y1-y2)             # distance via manhattan
    return c

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.val = PATH
        draw()
        
def algorithm(draw, net0, net1, start, end):
    if start is None or end is None:
        print("rah")
        return
    count = 0
    open_set = PriorityQueue()  # (f, count, node)
    open_set.put((0, count, start))
    came_from = {}
    all_nodes = net0.nodes + net1.nodes
    f_score = {node: float('inf') for row in all_nodes for node in row}
    g_score = {node: float('inf') for row in all_nodes for node in row}
    
    f_score[start] = h(start.get_pos(), end.get_pos())
    g_score[start] = 0
    
    open_set_hash = {start}
    
    while not open_set.empty():
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        current = open_set.get()[2]  # gets the node from (f, count, node)
        open_set_hash.remove(current)
        if current == end:
            reconstruct_path(came_from, current, draw)
            start.val = START
            end.val = END
            return True
        
        # for neighbour in net0.get_neighbours(current[0], current[1]):
        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1  # all weights are 1 FOR NOW
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.val = OPEN
        draw()
        if current != start:
            neighbour.val = CLOSED
    return False

# def update_screen(net0, net1):
#     pass

def is_toplefter(origin_node, other_node):
    if origin_node.y < other_node.y:
        return True
    if origin_node.x < other_node.x:
        return True
    return False

def draw_edges(net0, net1):
    for row in net0.nodes + net1.nodes:
        for node in row:
            for neighbour in filter(lambda n:is_toplefter(node, n), node.neighbours):
                colour = pygame.Color('black')
                line_w = 1
                if (node.val == PATH or node.val == START or node.val == END) and (neighbour.val == PATH or neighbour.val == START or neighbour.val == END):
                    colour = legend[PATH]
                    line_w = 3
                pygame.draw.line(scr, colour, (node.x, node.y), (neighbour.x, neighbour.y), line_w)

def draw(net0, net1):
    for row in net0.nodes + net1.nodes:
        for node in row:
            node.draw()
    # net0.draw_gridlines()
    # net1.draw_gridlines()
    draw_edges(net0, net1)
    
def get_hovered_node(nodes):
    for row in nodes:
        for node in row:
            if node.hover: return node
    return False

def update_neighbours(net_outer, net_inner):
    for row in net_outer.nodes + net_inner.nodes:
        for node in row:
            node.neighbours = node.get_neighbours()
    update_cross_neighbours(net_outer, net_inner)

def update_cross_neighbours(net_outer, net_inner):
    for i, row in enumerate(net_inner.nodes):
        for j, node in enumerate(row):
            if node.val == BARRIER: 
                continue
            for m in range(2):
                for n in range(2):
                    if net_outer.nodes[i+m][j+n].val != BARRIER:
                        node.neighbours.append(net_outer.nodes[i+m][j+n])
                        net_outer.nodes[i+m][j+n].neighbours.append(node)

def main():
    clock = pygame.time.Clock()
    my_board = chessboard.Grid(50, vec2(200, 200), None)
    net0 = Network(200, 200, 9, 9, 50, pygame.Color('black'))
    net1 = Network(225, 225, 8, 8, 50, pygame.Color('blue'))
    
    start = None
    end = None
    
    started = False
    
    current_char = BARRIER
    
    while True:
        
        events = pygame.event.get()
        scr.fill('white')
        scr.blit(my_board.surf, my_board.offset)
        my_board.update(events)
        draw(net0, net1)
        for row in net0.nodes + net1.nodes:
            for node in row:
                node.update(events) 
        
        for ev in events:
            mouse_states = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            node = get_hovered_node(net0.nodes + net1.nodes)
            if (ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEMOTION) and node:
                if mouse_states[0]: # lmb
                    if current_char == START:
                        if start is not None:
                            start.val = EMPTY
                        start = node
                    elif node.val == START:
                        start = None
                    
                    if current_char == END:
                        if end is not None:
                            end.val = EMPTY
                        end = node
                    elif node.val == END:
                        start = None
                    
                    node.val = current_char
                elif mouse_states[2]:  # rmb
                    if node == START:
                        start = None
                    if node == END:
                        end = None
                    node.val = EMPTY
                update_neighbours(net0, net1)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:  # wall
                    current_char = BARRIER
                elif ev.key == pygame.K_2:  # start
                    current_char = START
                elif ev.key == pygame.K_3:  # end
                    current_char = END
                
                if ev.key == pygame.K_SPACE and not started:
                    update_neighbours(net0, net1)
                    started = True
                    algorithm(lambda: draw(net0, net1), net0, net1, start, end)
        
        
        
        pygame.display.update()
        clock.tick(60)
if __name__ == '__main__':
    main()