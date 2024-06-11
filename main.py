from stockfish import Stockfish
import visualizer as vz
import time

def parse_board_state(stockfish_board):
    board = []
    for idx, row in enumerate(stockfish_board.split('\n')[:-2]):
        if idx % 2 == 0: continue
        board.append([i.strip() for i in row[1:-3].split('|')])
        
    return board

def main():
    vz.run()
        
if __name__ == '__main__':
    main()