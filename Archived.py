"""Minimax Starting Code"""
# for move in self.order_pieces(board):
#     self.count += 1
#     board.push(move)
#     val = self.minimax(board, 1, -1, alpha, beta)
#     board.pop()
#
#     if val > best:
#         best = val
#         best_move = move
#
#     alpha = max(best, alpha)
#     if beta <= alpha and self.alpha_beta:
#         break

"""Main minimax code """
# if player > 0:
#     best = float('-inf')
#     for move in self.order_pieces(board):
#         self.count += 1
#         board.push(move)
#         best = max(self.minimax(board, depth + 1, -1, alpha, beta), best)
#         board.pop()
#
#         alpha = max(best, alpha)
#         if beta <= alpha and self.alpha_beta:
#             break
#     return best
#
# elif player < 0:
#     best = float('inf')
#     for move in self.order_pieces(board):
#         self.count += 1
#         board.push(move)
#         best = min(self.minimax(board, depth + 1, 1, alpha, beta), best)
#         board.pop()
#
#         beta = min(best, beta)
#         if beta <= alpha and self.alpha_beta:
#             break
#     return best

"""Fast Piece Value Calculator (No Look Up Boards)"""
# pieces = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
# colors = [chess.WHITE, chess.BLACK]
# for piece in pieces:
#     for color in colors:
#         if color:
#             multi = self.color
#         else:
#             multi = -self.color
#
#         amt = len(board.pieces(piece, color))
#         total += self.values.PIECE_VALUE[chess.piece_symbol(piece)] * multi * amt

"""Slow Piece Value Calculator (Stupid I think)"""
# for square in chess.SQUARES:
#     piece = board.piece_at(square)
#     if piece is None:
#         continue
#
#     if piece.symbol().isupper():
#         multi = self.color
#     else:
#         multi = -self.color
#
#     total += self.values.PIECE_VALUE[piece.symbol().lower()] * multi

"""Old Undo Code For Piece Table Calculation"""
# piece_two = board.piece_at(board.peek().to_square)
# move = board.pop()
# adjust = self.values.eval_table(piece_two, board.piece_at(move.from_square),
#                                 move.from_square, move.to_square, self.endgame)
# self.table_score -= adjust
#
# # For the case where a piece is captured due to a move
# if board.is_capture(move):
#     try:
#         color = board.piece_at(move.to_square).color
#         multi = 1 if color else - 1
#         p = board.piece_at(move.to_square).piece_type
#         captured = self.values.grab_value_table(move.to_square, self.endgame, color)[p]
#         self.table_score += captured * multi
#     except AttributeError:
#         print(board.gives_check(move), move)
#         print(board.unicode())

"""First Piece Ordering Code"""
# top = []
#         captures = []
#         checks = []
#         others = []
#         for move in board.legal_moves:
#             if move == iter_move:
#                 top.append(iter_move)
#             elif board.is_capture(move):
#                 captures.append(move)
#             elif board.gives_check(move):
#                 checks.append(move)
#             else:
#                 others.append(move)
#
#         return top + captures + checks + others
