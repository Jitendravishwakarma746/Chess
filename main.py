import sys

import pygame

from const import WIDTH, HEIGHT, FPS
from game import Game


class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("CHESS")
        self.clock = pygame.time.Clock()
        self.game = Game()

    def mainloop(self):
        screen = self.screen
        game = self.game

        while True:
            # `game` and its parts are re-read each frame because R replaces the board
            board = game.board
            dragger = game.dragger

            # ---- draw (back to front)
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_check(screen)
            game.show_moves(screen)
            game.show_hover(screen)
            game.show_pieces(screen)
            dragger.update_blit(screen)
            game.show_promotion(screen)
            game.show_status(screen)

            # ---- input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset()
                    elif event.key == pygame.K_t:
                        game.change_theme()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                elif board.promotion_square is not None:
                    # waiting for the player to choose a promotion piece
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        choice = game.promotion_click(event.pos)
                        if choice:
                            board.promote(choice)
                            game.next_turn()

                elif game.status != 'playing':
                    continue  # game over: only R / T / quit work

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    dragger.update_mouse(event.pos)
                    row, col = dragger.get_square()
                    piece = board.squares[row][col].piece
                    if piece is not None and piece.color == game.next_player:
                        board.calc_moves(piece, row, col)
                        dragger.save_position(row, col)
                        dragger.drag_piece(piece)

                elif event.type == pygame.MOUSEMOTION:
                    dragger.update_mouse(event.pos)
                    game.set_hover(*dragger.get_square())

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        row, col = dragger.get_square()
                        piece = dragger.piece
                        move = next((m for m in piece.moves
                                     if m.final.row == row and m.final.col == col), None)
                        dragger.undrag_piece()
                        if move is not None:
                            board.move(piece, move)
                            game.play_sound()
                            if board.promotion_square is None:
                                game.next_turn()
                        else:
                            piece.clear_moves()

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    Main().mainloop()
