import chess
import chess.svg

from time import perf_counter
from collections import deque

from TunedValues import TunedValues
from Zobrist import Zobrist


class Engine:
    def __init__(self, board: chess.Board, color: int = -1):
        self.color = color

        self.values = TunedValues()
        self.zobrist = Zobrist()

        self.zobrist.generate_numbers()
        self.zobrist.init_hash(board)
        self.transposition = dict()

        self.endgame = 0
        self.total_pieces = 0
        self.piece_value_count = self.count_pieces(board)
        self.table_score = self.init_table(board)
        self.adjust_stack = deque()
        self.capture_stack = deque()

        self.alpha_beta = True
        self.quiescence_search_active = True

        self.count = 0
        self.recent_time = 0
        self.depth = 0
        self.diagnostics = dict()
        self.init_diagnostics()
    
    def init_table(self, board: chess.Board):
        score = 0
        total = 0
        for square in chess.SQUARES:
            if board.piece_at(square) is not None:
                total += 1

                p = board.piece_at(square).piece_type
                color = board.piece_at(square).color
                multi = self.color if color else -self.color

                square = self.values.coord_change[square]
                adj = self.values.grab_value_table(square, self.endgame, color)[p] * multi

                score += adj
        self.total_pieces = 32 - total

        return score
    
    def store_transposition(self, value, move, depth):
        if self.zobrist.zobrist_hash in self.transposition:
            position = self.transposition[self.zobrist.zobrist_hash]
            if depth > position[2] and value not in (float('inf'), float('-inf')):
                self.transposition[self.zobrist.zobrist_hash] = (value, move, depth)
        else:
            self.transposition[self.zobrist.zobrist_hash] = (value, move, depth)

    def start(self, board: chess.Board):
        best_move = None

        self.count = 0
        start = perf_counter()

        alpha = float('-inf')
        beta = float('inf')

        go = True

        for i in range(1, 200, 2):
            if not go:
                break

            self.depth = i
            if self.zobrist.zobrist_hash in self.transposition:
                position = self.transposition[self.zobrist.zobrist_hash]
                if position[2] >= i:
                    best_move = position[1]
                    continue

            alpha = float('-inf')
            beta = float('inf')

            for move in self.order_pieces(board, best_move):
                if perf_counter() - start >= 1:
                    go = False
                    break

                self.count += 1
                self.push(board, move)
                score = -self.search(board, i, -1, -beta, -alpha)
                self.undo(board)

                if score > alpha or score == alpha == float('-inf'):
                    best_move = move
                    alpha = score

        self.recent_time = perf_counter() - start
        self.update_diagnostics(self.count, self.recent_time, best_move, alpha,
                                self.evaluate(board), self.count_pieces(board),
                                self.endgame, self.depth, self.zobrist.zobrist_hash)
        
        self.store_transposition(alpha, best_move, self.depth)
        print(len(self.transposition))
        return best_move

    def search(self, board: chess.Board, depth: int, player: int, alpha: float, beta: float):
        good_move = None

        if depth == 0:
            if self.quiescence_search_active:
                qui_val = self.quiescence_search(board, player, alpha, beta, 0)
                return qui_val
            return self.evaluate(board)

        if self.zobrist.zobrist_hash in self.transposition:
            position = self.transposition[self.zobrist.zobrist_hash]
            if position[2] >= depth:
                best_move = position[1]
                return position[0]

        for move in self.order_pieces(board):
            self.count += 1
            self.push(board, move)
            score = -self.search(board, depth - 1, -player, -beta, -alpha)
            self.undo(board)

            if score >= beta:
                self.store_transposition(beta, move, depth)
                return beta
            if score > alpha:
                good_move = move
                alpha = score

        self.store_transposition(alpha, good_move, depth)
        return alpha

    def quiescence_search(self, board: chess.Board, player: int, alpha: float, beta: float, depth: int):
        evaluation = self.evaluate(board)

        # if depth >= 10:
        #     return evaluation

        if evaluation >= beta:
            return beta
        alpha = max(alpha, evaluation)

        for move in self.quiescence_pieces(board):
            self.count += 1
            self.push(board, move)
            score = -self.quiescence_search(board, -player, -beta, -alpha, depth+1)
            self.undo(board)

            if score >= beta:
                return score
            alpha = max(alpha, score)

        return alpha

    def quiescence_pieces(self, board: chess.Board):
        captures = []
        checks = []
        for move in board.legal_moves:
            if board.is_capture(move):
                captures.append(move)
            elif board.gives_check(move):
                checks.append(move)

        def piece_key(mv):
            mov = mv.uci()
            first = mov[:2]
            second = mov[2:4]

            one = self.values.PIECE_VALUE[board.piece_at(chess.SQUARES[chess.parse_square(first)]).symbol().lower()]
            two = 100
            if board.piece_at(chess.SQUARES[chess.parse_square(second)]) is not None:
                two = self.values.PIECE_VALUE[
                    board.piece_at(chess.SQUARES[chess.parse_square(second)]).symbol().lower()
                ]

            return two / one

        output = sorted(captures, key=piece_key, reverse=True) + checks
        return output

    def order_pieces(self, board: chess.Board, iter_move: chess.Move = None):
        top = []
        moves = []
        for move in board.legal_moves:
            if move == iter_move:
                top.append(iter_move)
            else:
                moves.append(move)

        def move_key(mov: chess.Move):
            score = 0

            if board.is_capture(mov):
                score += 50
            if board.gives_check(mov):
                score += 25

            self.special_move(board, move)
            if self.zobrist.zobrist_hash in self.transposition:
                score += self.transposition[self.zobrist.zobrist_hash][0]
            self.special_undo(board)

            return score

        return top + sorted(moves, key=move_key, reverse=True)

    def push(self, board: chess.Board, move: chess.Move):
        adjust = 0
        # For the case where a piece is captured due to a move
        captured_piece = None
        captured_square = None
        if board.is_capture(move):
            addon = 0
            if board.is_en_passant(move):
                addon = -8 if board.piece_at(move.from_square).color else 8

            color = board.piece_at(move.to_square + addon).color
            multi = 1 if color else - 1
            p = board.piece_at(move.to_square + addon)

            captured_piece = p
            captured_square = move.to_square + addon

            p = p.piece_type
            captured = self.values.grab_value_table(move.to_square + addon, self.endgame, color)[p]
            adjust = -captured * multi

            self.total_pieces += 1
            self.endgame = min(1.0, self.total_pieces / 26)

            val = self.values.PIECE_VALUE[board.piece_at(move.to_square + addon).symbol().lower()]
            self.piece_value_count -= val * (self.color if color else -self.color)
            self.capture_stack.append(board.piece_at(move.to_square + addon))
        else:
            self.capture_stack.append(None)

        piece_two = board.piece_at(move.from_square)

        if board.is_kingside_castling(move) and piece_two.color:
            adjust += self.values.eval_table(chess.Piece(6, True), chess.Piece(6, True),
                                             7, 5, self.endgame, self.color)

            self.zobrist.update_rook_hash(7, 5, piece_two.color)
        elif board.is_queenside_castling(move) and piece_two.color:
            adjust += self.values.eval_table(chess.Piece(6, True), chess.Piece(6, True),
                                             0, 3, self.endgame, self.color)

            self.zobrist.update_rook_hash(0, 3, piece_two.color)
        elif board.is_kingside_castling(move):
            adjust += self.values.eval_table(chess.Piece(6, False), chess.Piece(6, False),
                                             7, 5, self.endgame, self.color)

            self.zobrist.update_rook_hash(63, 61, piece_two.color)
        elif board.is_queenside_castling(move):
            adjust += self.values.eval_table(chess.Piece(6, False), chess.Piece(6, False),
                                             0, 3, self.endgame, self.color)

            self.zobrist.update_rook_hash(56, 59, piece_two.color)

        board.push(move)
        adjust += self.values.eval_table(piece_two, board.piece_at(move.to_square),
                                         move.from_square, move.to_square, self.endgame, self.color)
        self.zobrist.update_hash(board, move, piece_two, captured_piece, captured_square)
        self.adjust_stack.append(adjust)
        self.table_score += adjust

    def undo(self, board: chess.Board):
        self.table_score -= self.adjust_stack.pop()
        self.zobrist.undo_hash()
        board.pop()

        piece = self.capture_stack.pop()
        if piece is not None:
            multi = self.color if piece.color else -self.color
            self.piece_value_count += self.values.PIECE_VALUE[piece.symbol().lower()] * multi
            self.total_pieces -= 1
        self.endgame = min(1.0, self.total_pieces / 20)

    def special_move(self, board: chess.Board, move: chess.Move):
        captured_piece = None
        captured_square = None
        if board.is_capture(move):
            addon = 0
            if board.is_en_passant(move):
                addon = -8 if board.piece_at(move.from_square).color else 8

            captured_piece = board.piece_at(move.to_square + addon)
            captured_square = move.to_square + addon

        piece_two = board.piece_at(move.from_square)
        board.push(move)
        self.zobrist.update_hash(board, move, piece_two, captured_piece, captured_square)

    def special_undo(self, board: chess.Board):
        self.zobrist.undo_hash()
        board.pop()

    def evaluate(self, board: chess.Board):
        player = -1 if board.turn else 1

        if board.outcome() is not None:
            if board.outcome().winner is None:
                return 0
            else:
                return player * float('inf') * -self.color

        total = 0

        total += self.piece_value_count
        total += self.table_score

        return total * player * -self.color

    def count_pieces(self, board: chess.Board):
        total = 0
        pieces = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
        colors = [chess.WHITE, chess.BLACK]
        for piece in pieces:
            for color in colors:
                if color:
                    multi = self.color
                else:
                    multi = -self.color

                amt = len(board.pieces(piece, color))
                total += self.values.PIECE_VALUE[chess.piece_symbol(piece)] * multi * amt
        return total

    # The weird diagnostics corner
    def init_diagnostics(self):
        self.diagnostics = {
            'Moves Examined': 0,
            'Time Elapsed': 0,
            'Test Move': 0,
            'Search Evaluation': 0,
            'Board Evaluation': 0,
            'Piece Count: ': 0,
            'Endgame Score': 0,
            'Depth': 0,
            'Zobrist Hash': 0
        }

    def update_diagnostics(self, *args):
        for i, key in enumerate(self.diagnostics.keys()):
            self.diagnostics[key] = args[i]

    def get_diagnostics_as_list(self):
        output = []
        for key, value in self.diagnostics.items():
            if isinstance(value, float):
                output.append(f"{key}: {round(value, 2)}")
            else:
                output.append(f"{key}: {value}")
        return output
