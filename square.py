from const import ROW, COL


class Square:
    def __init__(self, row, col, piece=None):
        self.row = row
        self.col = col
        self.piece = piece

    def __eq__(self, other):
        return isinstance(other, Square) and self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def has_piece(self):
        return self.piece is not None

    def isempty(self):
        return not self.has_piece()

    def has_team_piece(self, color):
        return self.has_piece() and self.piece.color == color

    def has_rival_piece(self, color):
        return self.has_piece() and self.piece.color != color

    def isempty_or_rival(self, color):
        return self.isempty() or self.has_rival_piece(color)

    @staticmethod
    def in_range(*args):
        return all(0 <= a < ROW for a in args)  # ROW == COL == 8

    @staticmethod
    def get_alphacol(col):
        return "abcdefgh"[col]
