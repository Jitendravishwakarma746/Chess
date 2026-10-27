# CHESSGAME

Two-player chess in Python + Pygame.

## Run
    pip install -r requirements.txt
    python main.py        # works from any folder

## Controls
- Drag a piece with the left mouse button; legal squares are highlighted.
- R restart, T change board theme, Esc quit.
- Pawn promotion: click the piece you want in the popup.

## Rules implemented
All piece moves, captures, castling, en passant, promotion, check / pinned
pieces (only legal moves are allowed), checkmate, stalemate and draw by
insufficient material.

## Tests
    python ../test_rules.py   # perft counts vs. known-correct numbers (no pygame needed)
