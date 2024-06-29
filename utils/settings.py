import pygame as pg
from enum import Enum
from utils.paths import dir_images, dir_sound
from os import path


class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3


class Settings:
    _instance = None

    def __new__(cls, screen: pg.Surface = None):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialise(screen)
        elif screen is not None:
            print("Warning: screen parameter is already set and cannot be changed.")
        return cls._instance

    def _initialise(self, screen: pg.Surface):
        if screen is None:
            raise ValueError("Screen parameter is required during the first initialization.")
        else:
            self.screen = screen
        self.background_img: pg.Surface
        self.font_size_base: int
        self.play_music = True
        self.play_sound = True
        self.player_name = 'Anonymous'
        self.difficulty = Difficulty.NORMAL

        pg.mixer.music.load(path.join(dir_sound, 'planetary_paths.mp3'), 'planet_paths')
        self.background_img = pg.transform.scale(pg.image.load(path.join(dir_images, 'background.jpeg')),
                                                 (self.screen.get_width(), self.screen.get_height()))
        self.font_size_base = round(self.screen.get_height() / 25)
