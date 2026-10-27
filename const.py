import os

# folder that contains this file, so assets load no matter where you run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# screen dimension
WIDTH = 640
HEIGHT = 640

# board dimension
ROW = 8
COL = 8
SQSIZE = WIDTH // COL

ALPHACOL = "abcdefgh"

# pieces are drawn smaller than the square so they sit inside it with a margin
PIECE_SIZE = int(SQSIZE * 0.8)

FPS = 60
