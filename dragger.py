import pygame

from const import SQSIZE, PIECE_SIZE


class Dragger:
    def __init__(self):
        self.mouseX = 0
        self.mouseY = 0
        self.initial_row = 0
        self.initial_col = 0
        self.piece = None
        self.dragging = False
        self._images = {}  # cache so the PNG is not reloaded every frame

    def update_mouse(self, pos):
        self.mouseX, self.mouseY = pos

    def get_square(self):
        """Row and col of the square currently under the mouse (pixel -> grid)."""
        return self.mouseY // SQSIZE, self.mouseX // SQSIZE

    def save_position(self, initial_row, initial_col):
        self.initial_row = initial_row
        self.initial_col = initial_col

    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True

    def undrag_piece(self):
        self.piece = None
        self.dragging = False

   
    def _get_image(self, path):
        if path not in self._images:
            img = pygame.image.load(path).convert_alpha()
            self._images[path] = pygame.transform.smoothscale(img, (PIECE_SIZE, PIECE_SIZE))
        return self._images[path]

    def update_blit(self, surface):
        """Draw the dragged piece centred on the cursor. Call this LAST so it sits on top."""
        if not self.dragging or self.piece is None:
            return
        image = self._get_image(self.piece.texture)
        self.piece.texture_rect = image.get_rect(center=(self.mouseX, self.mouseY))
        surface.blit(image, self.piece.texture_rect)
