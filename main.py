from stockfish import Stockfish
from visualizer import Visualizer

stockfish = Stockfish(path="stockfish/stockfish")

def parse_board_state(stockfish_fen):
    board = []
    rows, meta = stockfish_fen.split(' ', 1)
    turn_colour, castling, enpassant, halfmove_clock, fullmove_num = meta.split(' ')
    for r in rows.split('/'):
        board.append(''.join([char if not char.isdigit() else ' '*int(char) for char in r]))
    return board

def main():
    stockfish.set_fen_position('r3q1k1/pp3ppp/2n5/3p4/3P1Bn1/1PQN4/2P2PPP/R5K1 w - - 0 20')
    stockfish.get_evaluation()
    fen_board = stockfish.get_fen_position()
    board = parse_board_state(fen_board)
    
    vz = Visualizer(stockfish)
    vz.run(board)
        
if __name__ == '__main__':
    main()