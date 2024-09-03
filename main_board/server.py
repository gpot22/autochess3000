import websocket
import asyncio

from visualizer import pathfinder, chessboard
from visualizer.pathfinder import Pathfinder, Node_Grid, Network, Node, update_neighbours
# from pathfinder import Car

ws = websocket.WebSocket()
ws.connect('ws://10.0.0.229/ws')

async def main():
    print(ws.recv())
    await ws.send("bye")
    
    
def init_pathfinder():
    node_grid_outer = Node_Grid(25, 125, 8, 12, 50)
    node_grid_inner = Node_Grid(50, 150, 7, 11, 50)
    nodes = node_grid_outer.nodes + node_grid_inner.nodes
    network = Network(0, 0, nodes, lambda: update_neighbours(node_grid_outer, node_grid_inner), 0, 0)
    pathfinder = Pathfinder(network)
    # my_board = chessboard.Grid(50, vec2(100, 100), None)
    
def init_cars():
    car0 = {
        'x': 0,
        'y': 0
    }
    
    car1 = {
        'x': 0,
        'y': 0
    }
    
    return [car0, car1]

if __name__ == '__main__':
    asyncio.run(main())