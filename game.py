import os

import pygame

from const import ROW, COL, SQSIZE, PIECE_SIZE, WIDTH, HEIGHT, ALPHACOL, ASSETS_DIR
from board import Board
from dragger import Dragger
from config import Config

PROMO_CHOICES = ('queen', 'rook', 'bishop', 'knight')


class Game:
    def __init__(self):
        self.config = Config()          # survives resets, so theme choice is kept
        self.font = None
        self.big_font = None
        self.reset()

    def reset(self):
        self.board = Board()
        self.dragger = Dragger()
        self.next_player = 'white'
        self.hovered_sqr = None
        self.status = 'playing'         # 'playing' | 'checkmate' | 'stalemate' | 'draw'
        self.winner = None
        self.in_check = False
        self._images = {}

    # ------------------------------------------------------------- helpers
    def _fonts(self):
        if self.font is None:
            self.font = pygame.font.SysFont('arial', 14, bold=True)
            self.big_font = pygame.font.SysFont('arial', 44, bold=True)
        return self.font, self.big_font

    def _get_image(self, path):
        if path not in self._images:
            img = pygame.image.load(path).convert_alpha()
            self._images[path] = pygame.transform.smoothscale(img, (PIECE_SIZE, PIECE_SIZE))
        return self._images[path]

    def _square_color(self, row, col, light, dark):
        return light if (row + col) % 2 == 0 else dark

    # ------------------------------------------------------------- drawing
    def show_bg(self, surface):
        theme = self.config.theme
        font, _ = self._fonts()
        for row in range(ROW):
            for col in range(COL):
                color = self._square_color(row, col, theme.light, theme.dark)
                pygame.draw.rect(surface, color, (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE))
                # coordinates: ranks down the left edge, files along the bottom
                label_color = theme.dark if (row + col) % 2 == 0 else theme.light
                if col == 0:
                    lbl = font.render(str(ROW - row), True, label_color)
                    surface.blit(lbl, (4, row * SQSIZE + 4))
                if row == ROW - 1:
                    lbl = font.render(ALPHACOL[col], True, label_color)
                    surface.blit(lbl, (col * SQSIZE + SQSIZE - 12, HEIGHT - 18))

    def show_last_move(self, surface):
        move = self.board.last_move
        if move is None:
            return
        theme = self.config.theme
        for sq in (move.initial, move.final):
            color = self._square_color(sq.row, sq.col, theme.light_last, theme.dark_last)
            pygame.draw.rect(surface, color, (sq.col * SQSIZE, sq.row * SQSIZE, SQSIZE, SQSIZE))

    def show_check(self, surface):
        if not self.in_check:
            return
        pos = self.board.find_king(self.next_player)
        if pos:
            r, c = pos
            pygame.draw.rect(surface, (220, 50, 50), (c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE))

    def show_moves(self, surface):
        if not self.dragger.dragging:
            return
        theme = self.config.theme
        for move in self.dragger.piece.moves:
            f = move.final
            color = self._square_color(f.row, f.col, theme.light_move, theme.dark_move)
            pygame.draw.rect(surface, color, (f.col * SQSIZE, f.row * SQSIZE, SQSIZE, SQSIZE))

    def show_hover(self, surface):
        if self.hovered_sqr is not None:
            r, c = self.hovered_sqr
            pygame.draw.rect(surface, self.config.theme.hover,
                             (c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE), 3)

    def show_pieces(self, surface):
        for row in range(ROW):
            for col in range(COL):
                piece = self.board.squares[row][col].piece
                if piece is None or piece is self.dragger.piece:
                    continue  # the dragged piece is drawn by the dragger
                image = self._get_image(piece.texture)
                piece.texture_rect = image.get_rect(
                    center=(col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2))
                surface.blit(image, piece.texture_rect)

    # ---- promotion picker
    def promotion_rects(self):
        """Four clickable rectangles, one per promotion choice, centred on the board."""
        total = 4 * SQSIZE
        x0 = (WIDTH - total) // 2
        y0 = (HEIGHT - SQSIZE) // 2
        return [pygame.Rect(x0 + i * SQSIZE, y0, SQSIZE, SQSIZE) for i in range(4)]

    def show_promotion(self, surface):
        if self.board.promotion_square is None:
            return
        _, big = self._fonts()
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 140))
        surface.blit(shade, (0, 0))
        r, c = self.board.promotion_square
        color = self.board.squares[r][c].piece.color
        for name, rect in zip(PROMO_CHOICES, self.promotion_rects()):
            pygame.draw.rect(surface, (240, 240, 240), rect)
            pygame.draw.rect(surface, (60, 60, 60), rect, 2)
            img = self._get_image(os.path.join(ASSETS_DIR, f'{color}_{name}.png'))
            surface.blit(img, img.get_rect(center=rect.center))

    def promotion_click(self, pos):
        """Return the piece name clicked in the picker, or None."""
        for name, rect in zip(PROMO_CHOICES, self.promotion_rects()):
            if rect.collidepoint(pos):
                return name
        return None

    def show_status(self, surface):
        if self.status == 'playing':
            return
        font, big = self._fonts()
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 120))
        surface.blit(shade, (0, 0))
        if self.status == 'checkmate':
            text = f'Checkmate - {self.winner.capitalize()} wins'
        elif self.status == 'stalemate':
            text = 'Stalemate - draw'
        else:
            text = 'Draw - insufficient material'
        label = big.render(text, True, (255, 255, 255))
        surface.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        hint = font.render('Press R to play again', True, (230, 230, 230))
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))

    # ------------------------------------------------------------ game flow
    def set_hover(self, row, col):
        self.hovered_sqr = (row, col) if 0 <= row < ROW and 0 <= col < COL else None

    def play_sound(self):
        self.config.move_sound.play()

    def change_theme(self):
        self.config.change_theme()

    def next_turn(self):
        """Hand the move to the other player and work out check / mate / draw."""
        self.next_player = 'black' if self.next_player == 'white' else 'white'
        b = self.board
        self.in_check = b.in_check(self.next_player)
        if not b.has_legal_moves(self.next_player):
            if self.in_check:
                self.status = 'checkmate'
                self.winner = 'black' if self.next_player == 'white' else 'white'
            else:
                self.status = 'stalemate'
        elif b.insufficient_material():
            self.status = 'draw'
