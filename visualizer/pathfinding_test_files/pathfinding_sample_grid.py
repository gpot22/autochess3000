import pygame
pygame.init()
vec2 = pygame.math.Vector2

import json

import sys
from queue import PriorityQueue

BARRIER = '#'
START = 'i'
END = 'x'
PATH = 'o'
OPEN = '+'
CLOSED = '-'

legend = {
    BARRIER: pygame.Color('black'),
    START: pygame.Color('cyan'),
    END: pygame.Color('orange'),
    PATH: pygame.Color('purple'),
    OPEN: pygame.Color('green'),
    CLOSED: pygame.Color('red')
}

class Grid:
    def __init__(self, x, y, width, height, tile_size):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.column_count = width//tile_size
        self.row_count = height//tile_size
        self.tile_size = tile_size
        
        # self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = pygame.Rect(x, y, width, height)
        
        # self.rect.x = x
        # self.rect.y = y
        
        self.line_colour = pygame.Color('black')
        # self.wall_colour = pygame.Color('black')
        # self.point_colour = pygame.Color('green')
        # self.path_colour = pygame.Color('red')
        
        self.tiles = self._build()
        self.update(pygame.display.get_surface())
        
    def _build(self):
        tiles = []
        for _ in range(self.row_count):
            tiles.append([' ' for _ in range(self.column_count)])
        return tiles
            
    def _draw_gridlines(self, scr):
        pygame.draw.rect(scr, self.line_colour, self.rect, 1)
        # pygame.draw.rect(self.image, self.line_colour, pygame.Rect(0, 0, self.width, self.height), 1)
        for i in range(1, self.column_count): # vertical
            pygame.draw.line(scr, self.line_colour, (self.x+i*self.tile_size, self.y), (self.x+i*self.tile_size, self.y+self.height))
        for i in range(1, self.row_count): # vertical
            pygame.draw.line(scr, self.line_colour, (self.x, self.y+i*self.tile_size), (self.x+self.width, self.y+i*self.tile_size))
        
    def update(self, scr):
        # self.image.fill('white')
        scr.fill('white')
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                if tile != ' ':
                    pygame.draw.rect(scr, legend[tile], pygame.Rect(self.x+j*self.tile_size, self.y+i*self.tile_size, self.tile_size, self.tile_size))
                # if tile == '#':
                #     pygame.draw.rect(self.image, self.wall_colour, pygame.Rect(j*self.tile_size, i*self.tile_size, self.tile_size, self.tile_size))
        self._draw_gridlines(scr)
        # for i in self.column_count:
        #     for j in self.row_count:
    
    def xy_to_ij(self, x, y):
        i = (y - self.rect.y) // self.tile_size
        j = (x - self.rect.x) // self.tile_size
        return i, j
    
    def show_tiles(self):
        with open('grid.json', 'w') as f:
            json.dump(self.tiles, f, indent=4)
            
    def clear(self):
        self.tiles = self._build()
        
    def reset(self):
        for i in range(self.row_count):
            for j in range(self.column_count):
                if self.tiles[i][j] == OPEN or self.tiles[i][j] == CLOSED or self.tiles[i][j] == PATH:
                    self.tiles[i][j] = ' '
        
    def is_barrier(self, c):
        return c == BARRIER
        
    def get_neighbours(self, i, j):
        neighbours = []
        if i > 0 and not self.tiles[i-1][j] == BARRIER:  # above
            neighbours.append((i-1, j))
            
        if i < self.row_count - 1 and not self.tiles[i+1][j] == BARRIER:  # below
            neighbours.append((i+1, j))
        
            
        if j > 0 and not self.tiles[i][j-1] == BARRIER:  # left
            neighbours.append((i, j-1))
            
        if j < self.column_count - 1 and not self.tiles[i][j+1] == BARRIER:  # right
            neighbours.append((i, j+1))
        return neighbours
        
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def reconstruct_path(came_from, current, draw, grid):
    while current in came_from:
        current = came_from[current]
        grid.tiles[current[0]][current[1]] = PATH
        draw()

def algorithm(draw, grid, start, end):
    if start is None or end is None:
        print("rah")
        return
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    f_score = { (i, j) : float('inf') for i, row in enumerate(grid.tiles) for j, _ in enumerate(row)}
    g_score = { (i, j) : float('inf') for i, row in enumerate(grid.tiles) for j, _ in enumerate(row)}
    
    f_score[start] = h((*start,), (*end,))
    g_score[start] = 0
    
    open_set_hash = {start}  # keep track of all items in the priority queue, since you cant check if something is inside of the queue
    
    while not open_set.empty():
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        current = open_set.get()[2]  # gets the node = (i, j, tile)
        open_set_hash.remove(current)
        if current == end:
            reconstruct_path(came_from, end, draw, grid)
            grid.tiles[start[0]][start[1]] = START
            grid.tiles[end[0]][end[1]] = END
            return True
        
        for neighbour in grid.get_neighbours(current[0], current[1]):
            temp_g_score = g_score[current] + 1  # cuz all weights are 1
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h((*neighbour,), (*end,))
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    grid.tiles[neighbour[0]][neighbour[1]] = OPEN
        draw()
        if current != start:
            grid.tiles[neighbour[0]][neighbour[1]] = CLOSED
    return False

def update_screen(grid, scr):
    grid.update(scr)
    # scr.blit(grid.image, grid.rect)
    pygame.display.update()
    
def main():
    scr_w, scr_h = 800, 800
    scr = pygame.display.set_mode((scr_w, scr_h))
    clock = pygame.time.Clock()
    
    grid = Grid(100, 100, 600, 600, 10)
    
    current_char = BARRIER
    
    started = False
    
    start = None
    end = None
    
    while True:
        scr.fill('white')
        
        for ev in pygame.event.get():
            mouse_states = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEMOTION) and grid.rect.collidepoint(mouse_pos): 
                coord = grid.xy_to_ij(*mouse_pos)
                if mouse_states[0]: # lmb
                    if current_char == START:
                        if start is not None:
                            grid.tiles[start[0]][start[1]] = ' '
                        start = coord
                    elif grid.tiles[coord[0]][coord[1]] == START:
                        start = None
                        
                    if current_char == END:
                        if end is not None:
                            grid.tiles[end[0]][end[1]] = ' '
                        end = coord
                    elif grid.tiles[coord[0]][coord[1]] == END:
                        end = None
                        
                    grid.tiles[coord[0]][coord[1]] = current_char
                elif mouse_states[2]:  # rmb
                    if grid.tiles[coord[0]][coord[1]] == START:
                        start = None
                    if grid.tiles[coord[0]][coord[1]] == END:
                        end = None
                        
                    grid.tiles[coord[0]][coord[1]] = ' '
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:  # wall
                    current_char = BARRIER
                elif ev.key == pygame.K_2:  # start
                    current_char = START
                elif ev.key == pygame.K_3:  # end
                    current_char = END
                
                if ev.key == pygame.K_p:
                    grid.show_tiles()
                elif ev.key == pygame.K_c:
                    grid.clear()
                elif ev.key == pygame.K_r:
                    grid.reset()
                elif ev.key == pygame.K_SPACE and not started:
                    started = True
                    algorithm(lambda: update_screen(grid, scr), grid, start, end)
                    started = False
        grid.update(scr)
        # scr.blit(grid.image, grid.rect)
        
        pygame.display.update()
        clock.tick(60)

        

if __name__ == '__main__':
    main()
                