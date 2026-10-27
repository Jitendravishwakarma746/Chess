from const import ROW, COL
from square import Square
from piece import Pawn, Knight, Bishop, Rook, Queen, King
from move import Move


class Board:
    def __init__(self):
        self.squares = [[0] * COL for _ in range(ROW)]
        self.last_move = None
        self.promotion_square = None  # (row, col) of a pawn waiting to be promoted

        self._create()
        self._addpieces('white')
        self._addpieces('black')

    # ------------------------------------------------------------------ setup
    def _create(self):
        for row in range(ROW):
            for col in range(COL):
                self.squares[row][col] = Square(row, col)

    def _addpieces(self, color):
        if color == 'white':
            row_pawn, row_other = (6, 7)
        else:
            row_pawn, row_other = (1, 0)

        for col in range(COL):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))
        self.squares[row_other][4] = Square(row_other, 4, King(color))

    # ------------------------------------------------------------- executing
    def valid_move(self, piece, move):
        return move in piece.moves

    def move(self, piece, move):
        """Execute a move that has already been validated. Returns the captured piece (or None)."""
        initial, final = move.initial, move.final
        target = self.squares[final.row][final.col]
        captured = target.piece

        # an en passant flag only lasts for one turn
        was_ep = {}
        for r in range(ROW):
            for c in range(COL):
                p = self.squares[r][c].piece
                if isinstance(p, Pawn):
                    p.en_passant = False

        if isinstance(piece, Pawn):
            # en passant capture: pawn moves diagonally onto an empty square
            if initial.col != final.col and captured is None:
                victim = self.squares[initial.row][final.col]
                captured = victim.piece
                victim.piece = None
            # two-square jump: can be captured en passant next turn
            if abs(final.row - initial.row) == 2:
                piece.en_passant = True

        self.squares[initial.row][initial.col].piece = None
        target.piece = piece

        # promotion is completed later by promote() (the player picks the piece)
        if isinstance(piece, Pawn) and final.row in (0, ROW - 1):
            self.promotion_square = (final.row, final.col)

        # castling: the king moved two squares, so bring the rook across
        if isinstance(piece, King) and abs(final.col - initial.col) == 2:
            if final.col == 6:
                rook_from, rook_to = 7, 5
            else:
                rook_from, rook_to = 0, 3
            rook = self.squares[final.row][rook_from].piece
            self.squares[final.row][rook_from].piece = None
            self.squares[final.row][rook_to].piece = rook
            rook.moved = True

        piece.moved = True
        piece.clear_moves()
        self.last_move = move
        return captured

    def promote(self, name):
        """Replace the waiting pawn with a new piece ('queen', 'rook', 'bishop' or 'knight')."""
        row, col = self.promotion_square
        color = self.squares[row][col].piece.color
        cls = {'queen': Queen, 'rook': Rook, 'bishop': Bishop, 'knight': Knight}[name]
        new_piece = cls(color)
        new_piece.moved = True
        self.squares[row][col].piece = new_piece
        self.promotion_square = None

    # ------------------------------------------------------- move generation
    def calc_moves(self, piece, row, col, legal=True):
        """Fill piece.moves. legal=False gives pseudo-legal moves (ignores check)."""
        piece.clear_moves()
        for move in self._pseudo_moves(piece, row, col):
            if legal and self._leaves_king_in_check(piece, move):
                continue
            piece.add_move(move)
        if legal and isinstance(piece, King):
            for move in self._castling_moves(piece, row, col):
                piece.add_move(move)
        return piece.moves

    def _pseudo_moves(self, piece, row, col):
        sq = self.squares
        color = piece.color
        moves = []
        initial = Square(row, col)

        def add(r, c):
            moves.append(Move(initial, Square(r, c)))

        if isinstance(piece, Pawn):
            r = row + piece.dir
            if Square.in_range(r):
                if sq[r][col].isempty():
                    add(r, col)
                    r2 = r + piece.dir
                    if not piece.moved and Square.in_range(r2) and sq[r2][col].isempty():
                        add(r2, col)
                for dc in (-1, 1):
                    c = col + dc
                    if Square.in_range(c) and sq[r][c].has_rival_piece(color):
                        add(r, c)
                # en passant
                ep_row = 3 if color == 'white' else 4
                if row == ep_row:
                    for dc in (-1, 1):
                        c = col + dc
                        if Square.in_range(c) and sq[r][c].isempty():
                            side = sq[row][c].piece
                            if isinstance(side, Pawn) and side.color != color and side.en_passant:
                                add(r, c)

        elif isinstance(piece, Knight):
            for dr, dc in ((-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)):
                r, c = row + dr, col + dc
                if Square.in_range(r, c) and sq[r][c].isempty_or_rival(color):
                    add(r, c)

        elif isinstance(piece, King):
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if Square.in_range(r, c) and sq[r][c].isempty_or_rival(color):
                        add(r, c)

        else:  # sliding pieces: bishop, rook, queen
            if isinstance(piece, Bishop):
                dirs = ((-1, 1), (-1, -1), (1, 1), (1, -1))
            elif isinstance(piece, Rook):
                dirs = ((-1, 0), (0, 1), (1, 0), (0, -1))
            else:
                dirs = ((-1, 1), (-1, -1), (1, 1), (1, -1), (-1, 0), (0, 1), (1, 0), (0, -1))
            for dr, dc in dirs:
                r, c = row + dr, col + dc
                while Square.in_range(r, c):
                    if sq[r][c].isempty():
                        add(r, c)
                    else:
                        if sq[r][c].has_rival_piece(color):
                            add(r, c)
                        break  # blocked by any piece
                    r += dr
                    c += dc
        return moves

    def _castling_moves(self, king, row, col):
        moves = []
        if king.moved or col != 4 or self.in_check(king.color):
            return moves
        sq = self.squares
        initial = Square(row, col)
        # (rook column, columns that must be empty, column the king crosses, king target)
        for rook_col, empty, cross, target in ((0, (1, 2, 3), 3, 2), (7, (5, 6), 5, 6)):
            rook = sq[row][rook_col].piece
            if not isinstance(rook, Rook) or rook.moved or rook.color != king.color:
                continue
            if any(sq[row][c].has_piece() for c in empty):
                continue
            step = Move(initial, Square(row, cross))
            if self._leaves_king_in_check(king, step):
                continue
            final = Move(initial, Square(row, target))
            if self._leaves_king_in_check(king, final):
                continue
            moves.append(final)
        return moves

    # ------------------------------------------------------------ check logic
    def _leaves_king_in_check(self, piece, move):
        """Simulate the move, test for check, then put everything back exactly as it was."""
        sq = self.squares
        i, f = move.initial, move.final
        src, dst = sq[i.row][i.col], sq[f.row][f.col]
        moved_piece, taken = src.piece, dst.piece
        ep_square, ep_piece = None, None
        if isinstance(piece, Pawn) and i.col != f.col and taken is None:
            ep_square = sq[i.row][f.col]
            ep_piece = ep_square.piece
            ep_square.piece = None
        src.piece = None
        dst.piece = moved_piece
        try:
            return self.in_check(piece.color)
        finally:
            dst.piece = taken
            src.piece = moved_piece
            if ep_square is not None:
                ep_square.piece = ep_piece

    def find_king(self, color):
        for r in range(ROW):
            for c in range(COL):
                p = self.squares[r][c].piece
                if isinstance(p, King) and p.color == color:
                    return r, c
        return None

    def in_check(self, color):
        king_pos = self.find_king(color)
        if king_pos is None:
            return False
        kr, kc = king_pos
        for r in range(ROW):
            for c in range(COL):
                p = self.squares[r][c].piece
                if p is not None and p.color != color:
                    for m in self._pseudo_moves(p, r, c):
                        if m.final.row == kr and m.final.col == kc:
                            return True
        return False

    def has_legal_moves(self, color):
        for r in range(ROW):
            for c in range(COL):
                p = self.squares[r][c].piece
                if p is not None and p.color == color:
                    for m in self._pseudo_moves(p, r, c):
                        if not self._leaves_king_in_check(p, m):
                            return True
        return False

    def is_checkmate(self, color):
        return self.in_check(color) and not self.has_legal_moves(color)

    def is_stalemate(self, color):
        return not self.in_check(color) and not self.has_legal_moves(color)

    def insufficient_material(self):
        others = []
        for r in range(ROW):
            for c in range(COL):
                p = self.squares[r][c].piece
                if p is not None and not isinstance(p, King):
                    if isinstance(p, (Pawn, Rook, Queen)):
                        return False
                    others.append((p, r, c))
        if len(others) <= 1:
            return True  # K vs K, or K + one minor piece vs K
        if all(isinstance(p, Bishop) for p, _, _ in others):
            return len({(r + c) % 2 for _, r, c in others}) == 1  # bishops all on one colour
        return False
