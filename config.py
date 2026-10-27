import os

import pygame

from const import ASSETS_DIR


class Theme:
    def __init__(self, light, dark, light_move, dark_move, light_last, dark_last, hover):
        self.light = light
        self.dark = dark
        self.light_move = light_move   # valid-move highlight
        self.dark_move = dark_move
        self.light_last = light_last   # last-move highlight
        self.dark_last = dark_last
        self.hover = hover


class Sound:
    def __init__(self, path):
        self.sound = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.sound = pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError):
            pass  # no audio device: the game just stays silent

    def play(self):
        if self.sound is not None:
            self.sound.play()


class Config:
    def __init__(self):
        self.themes = [
            Theme((234, 235, 200), (119, 154, 88), (200, 70, 60), (190, 55, 50),
                  (244, 247, 116), (172, 195, 51), (180, 180, 180)),
            Theme((222, 227, 230), (140, 162, 173), (230, 100, 90), (205, 80, 70),
                  (235, 240, 150), (170, 190, 100), (200, 200, 200)),
            Theme((240, 217, 181), (181, 136, 99), (230, 100, 80), (200, 75, 60),
                  (250, 235, 120), (205, 175, 60), (200, 200, 200)),
        ]
        self.idx = 0
        self.theme = self.themes[self.idx]
        self.move_sound = Sound(os.path.join(ASSETS_DIR, 'move.wav'))

    def change_theme(self):
        self.idx = (self.idx + 1) % len(self.themes)
        self.theme = self.themes[self.idx]
