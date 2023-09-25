import chess


class TunedValues:
    def __init__(self):
        conv = [0, -8, -16, -24, -32, -40, -48, -56]
        self.coord_change = {i: 56 + conv[i//8] + i % 8 for i in range(64)}

        self.piece_multi = 2
        self.PIECE_VALUE = {
            'p': 100 * self.piece_multi,
            'n': 250 * self.piece_multi,
            'b': 300 * self.piece_multi,
            'r': 500 * self.piece_multi,
            'q': 900 * self.piece_multi,
            'k': 1
        }

        self.pawn_table = [
            60,   60,   60,   60,   60,   60,   60,   60,
            50,   50,   50,   50,   50,   50,   50,   50,
            40,   40,   40,   40,   40,   40,   40,   40,
            30,   30,   30,   70,   70,   30,   30,   30,
            20,   20,   20,  100,  150,   20,   20,   20,
             2,    4,    0,   15,    4,    0,    4,    2,
           -10,  -10,  -10,  -20,  -35,  -10,  -10,  -10,
             0,    0,    0,    0,    0,    0,    0,    0
        ]

        self.pawn_table_end = [
            9000, 9000, 9000, 9000, 9000, 9000, 9000, 9000,
             500,  500,  500,  500,  500,  500,  500,  500,
             300,  300,  300,  300,  300,  300,  300,  300,
              90,   90,   90,  100,  100,   90,   90,   90,
              70,   70,   70,   85,   85,   70,   70,   70,
              20,   20,   20,   20,   20,   20,   20,   20,
             -10,  -10,  -10,  -10,  -10,  -10,  -10,  -10,
               0,    0,    0,    0,    0,    0,    0,    0
        ]

        self.knight_table = [
            -20, -80, -60, -60, -60, -60, -80, -20,
            -80, -40,   0,   0,   0,   0, -40, -80,
            -60,   0,  20,  30,  30,  20,   0, -60,
            -60,  10,  30,  40,  40,  30,  10, -60,
            -60,   0,  30,  40,  40,  30,   0, -60,
            -60,  10,  30,   0,   0,  30,  10, -60,
            -80, -40,   0,  10,  10,   0, -40, -80,
            -20, -80, -60, -60, -60, -60, -80, -20
        ]

        self.bishop_table = [
            -40, -20, -20, -20, -20, -20, -20, -40,
            -20,   0,   0,   0,   0,   0,   0, -20,
            -20,   0,  10,  20,  20,  10,   0, -20,
            -20,  10,  10,  20,  20,  10,  10, -20,
            -20,   0,  20,  20,  20,  20,   0, -20,
            -20,  20,  20,  20,  20,  20,  20, -20,
            -20,  10,   0,   0,   0,   0,  10, -20,
            -40, -20, -20, -20, -20, -20, -20, -40
        ]

        self.rook_table = [
              0,  0,  0,  0,  0,  0,  0,   0,
             10, 20, 20, 20, 20, 20, 20,  10,
            -10,  0,  0,  0,  0,  0,  0, -10,
            -10,  0,  0,  0,  0,  0,  0, -10,
            -10,  0,  0,  0,  0,  0,  0, -10,
            -10,  0,  0,  0,  0,  0,  0, -10,
            -10,  0,  0,  0,  0,  0,  0, -10,
            -30, 30, 40, 10, 10,  0,  0, -30
        ]

        self.queen_table = [
            -40, -20, -20, -10, -10, -20, -20, -40,
            -20,   0,   0,   0,   0,   0,   0, -20,
            -20,   0,  10,  10,  10,  10,   0, -20,
            -10,   0,  10,  10,  10,  10,   0, -10,
              0,   0,  10,  10,  10,  10,   0, -10,
            -20,  10,  10,  10,  10,  10,   0, -20,
            -20,   0,  10,   0,   0,   0,   0, -20,
            -40, -20, -20, -10, -10, -20, -20, -40
        ]

        self.king_table = [
            -60, -80, -80, -20, -20, -80, -80, -60,
            -60, -80, -80, -20, -20, -80, -80, -60,
            -60, -80, -80, -20, -20, -80, -80, -60,
            -60, -80, -80, -20, -20, -80, -80, -60,
            -40, -60, -60, -80, -80, -60, -60, -40,
            -20, -40, -40, -40, -40, -40, -40, -20,
            -20, -20, -20, -20, -20, -20, -20, -20,
             40,  100,  20,   0,   0,  20,  100,  40
        ]

        self.king_table_end = [
            -200, -175, -175, -175, -175, -175, -175, -200,
            -175,  -50,  -50,  -50,  -50,  -50,  -50, -175,
            -175,  -50,   50,   50,   50,   50,  -50, -175,
            -175,  -50,   50,  150,  150,   50,  -50, -175,
            -175,  -50,   50,  100,  100,   50,  -50, -175,
            -175,  -50,   50,   50,   50,   50,  -50, -175,
            -175,  -50, - 50,  -50,  -50,  -50,  -50, -175,
            -200, -175, -175, -175, -175, -175, -175, -200
        ]

    def grab_value_table(self, space: chess.Square, endgame: float, color: chess.Color):
        if not color:
            space = (space % 8 + (7 - space // 8) * 8) % 64
        piece_table = {
            chess.PAWN: self.pawn_table[space] * (1 - endgame) + self.pawn_table_end[space] * endgame,
            chess.KNIGHT: self.knight_table[space],
            chess.BISHOP: self.bishop_table[space],
            chess.ROOK: self.rook_table[space],
            chess.QUEEN: self.queen_table[space],
            chess.KING: self.king_table[space] * (1 - endgame) + self.king_table_end[space] * endgame
        }
        return piece_table

    def eval_table(self, piece: chess.Piece, piece_two: chess.Piece,
                   old: chess.Square, new: chess.Square, endgame: float, color: int):
        pos1 = self.coord_change[int(old)]
        pos2 = self.coord_change[int(new)]
        multi = color

        if not piece.color:
            multi = -color

        p = piece.piece_type
        p2 = piece_two.piece_type
        return (self.grab_value_table(pos2, endgame, piece_two.color)[p2] -
                self.grab_value_table(pos1, endgame, piece.color)[p]) * multi
