import os

from const import ASSETS_DIR


class Piece:
    def __init__(self, name, color, value):
        self.name = name
        self.color = color
        self.value = value if color == 'white' else -value
        self.texture = os.path.join(ASSETS_DIR, f'{color}_{name}.png')  # path only
        self.texture_rect = None
        self.moves = []
        self.moved = False

    def add_move(self, move):
        self.moves.append(move)

    def clear_moves(self):
        self.moves = []

    def __str__(self):
        return f'{self.color} {self.name}'


class Pawn(Piece):
    def __init__(self, color):
        self.dir = -1 if color == 'white' else 1
        self.en_passant = False  # True right after this pawn made a 2-square jump
        super().__init__('pawn', color, 1.0)


class Knight(Piece):
    def __init__(self, color):
        super().__init__('knight', color, 3.0)


class Bishop(Piece):
    def __init__(self, color):
        super().__init__('bishop', color, 3.0)


class Rook(Piece):
    def __init__(self, color):
        super().__init__('rook', color, 5.0)


class Queen(Piece):
    def __init__(self, color):
        super().__init__('queen', color, 9.0)


class King(Piece):
    def __init__(self, color):
        super().__init__('king', color, 10000)
