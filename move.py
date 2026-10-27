class Move:
    """A move from one Square to another (coordinates are what matter)."""

    def __init__(self, initial, final):
        self.initial = initial
        self.final = final

    def __eq__(self, other):
        return (isinstance(other, Move)
                and self.initial == other.initial
                and self.final == other.final)

    def __hash__(self):
        return hash((self.initial, self.final))

    def __repr__(self):
        return (f'Move({self.initial.row},{self.initial.col} -> '
                f'{self.final.row},{self.final.col})')
