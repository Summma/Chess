import chess

import random
from collections import deque


class Zobrist:
    def __init__(self):
        self.seed = 12831283
        self.amt_numbers = 12 * 64 + 4 + 8 + 1

        self.zobrist_hash = 0
        self.array = []

        self.current_hash = 0
        self.hash_stack = deque()

    def generate_numbers(self):
        random.seed(self.seed)
        for i in range(self.amt_numbers):
            num = random.randint(2**63, 2**64-1)
            self.array.append(num)

    def hash_en_passant(self, board: chess.Board):
        if board.ep_square:
            if board.turn == chess.WHITE:
                ep_mask = chess.shift_down(chess.BB_SQUARES[board.ep_square])
            else:
                ep_mask = chess.shift_up(chess.BB_SQUARES[board.ep_square])
            ep_mask = chess.shift_left(ep_mask) | chess.shift_right(ep_mask)

            if ep_mask & board.pawns & board.occupied_co[board.turn]:
                return self.array[772 + chess.square_file(board.ep_square)]
        return 0

    def castling_hash(self, board: chess.Board):
        zobrist_hash = 0
        if board.has_kingside_castling_rights(chess.WHITE):
            zobrist_hash ^= self.array[768]
        if board.has_queenside_castling_rights(chess.WHITE):
            zobrist_hash ^= self.array[768 + 1]
        if board.has_kingside_castling_rights(chess.BLACK):
            zobrist_hash ^= self.array[768 + 2]
        if board.has_queenside_castling_rights(chess.BLACK):
            zobrist_hash ^= self.array[768 + 3]
        return zobrist_hash

    def init_hash(self, board: chess.Board):
        self.zobrist_hash = 0

        # Hashing every piece
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            index = square * 12 + (piece.piece_type - 1) * 2 + piece.color
            self.zobrist_hash ^= self.array[index]

        # Castling rights hash
        self.zobrist_hash ^= self.castling_hash(board)

        # En passant hash cus captures are weird in en passant
        self.zobrist_hash ^= self.hash_en_passant(board)

        # Turn hash
        self.zobrist_hash ^= self.array[780] if board.turn else 0

    def update_hash(self, board: chess.Board, move: chess.Move, old_piece: chess.Piece,
                    captured: chess.Piece, ep_square: int):
        old_square = move.from_square
        new_square = move.to_square
        
        new_piece = board.piece_at(new_square)

        index = old_square * 12 + (old_piece.piece_type - 1) * 2 + old_piece.color
        self.current_hash ^= self.array[index]

        index = new_square * 12 + (new_piece.piece_type - 1) * 2 + new_piece.color
        self.current_hash ^= self.array[index]

        if captured is not None:
            if ep_square != new_square:
                index = ep_square * 12 + (captured.piece_type - 1) * 2 + captured.color
                self.current_hash ^= self.array[index]
            else:
                index = new_square * 12 + (captured.piece_type - 1) * 2 + captured.color
                self.current_hash ^= self.array[index]

        self.current_hash ^= self.array[780]
        
        self.current_hash ^= self.hash_en_passant(board)
        self.current_hash ^= self.castling_hash(board)

        self.zobrist_hash ^= self.current_hash
        self.hash_stack.append(self.current_hash)
        self.current_hash = 0

    def update_rook_hash(self, old_square: int, new_square: int, color: bool):
        index = old_square * 12 + (chess.ROOK - 1) * 2 + color
        self.current_hash ^= self.array[index]

        index = new_square * 12 + (chess.ROOK - 1) * 2 + color
        self.current_hash ^= self.array[index]

    def undo_hash(self):
        self.zobrist_hash ^= self.hash_stack.pop()
