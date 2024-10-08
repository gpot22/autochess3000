from stockfish import Stockfish
from simulator import Simulator
# from pathfinder import Pathfinder

stockfish = Stockfish(path="stockfish/stockfish")

def parse_board_state(stockfish_fen):
    board = []
    rows, meta = stockfish_fen.split(' ', 1)
    turn_colour, castling, enpassant, halfmove_clock, fullmove_num = meta.split(' ')
    meta_data = ''
    for r in rows.split('/'):
        board.append(''.join([char if not char.isdigit() else ' '*int(char) for char in r]))
    return board, meta_data

def main():
    stockfish.set_fen_position('r3q1k1/pp3ppp/2n5/3p4/3P1Bn1/1PQN4/2P2PPP/R5K1 w - - 0 20')
    stockfish.get_evaluation()
    fen_board = stockfish.get_fen_position()
    board, _ = parse_board_state(fen_board)
    
    sim = Simulator(stockfish)
    sim.run(board)
    
if __name__ == '__main__':
    main()