from stockfish import Stockfish
import visualizer as vz

stockfish = Stockfish(path="stockfish/stockfish")

def parse_board_state(stockfish_board):
    board = []
    for idx, row in enumerate(stockfish_board.split('\n')[:-2]):
        if idx % 2 == 0: continue
        board.append([i.strip() for i in row[1:-3].split('|')])
        
    return board

def main():
    stockfish.set_position(["e2e4", "e7e6"])
    view_as_white = True
    sf_board = stockfish.get_board_visual(view_as_white)
    board = parse_board_state(sf_board)
    vz.run(board)
        
if __name__ == '__main__':
    main()