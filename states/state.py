import pygame as pg
from os import path
from enum import Enum

from utils.paths import dir_images, dir_sound

pg.init()


class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3


class State:
    _class_is_initialised = False
    _background_img: pg.Surface
    _font_size_base: int
    play_music = True
    play_sound = True
    player_name = None

    difficulty: Difficulty
    difficulty = Difficulty.NORMAL

    @staticmethod
    def initialise(screen: pg.Surface):
        if State._class_is_initialised:
            return

        pg.mixer.music.load(path.join(dir_sound, 'planetary_paths.mp3'), 'planet_paths')
        State._background_img = pg.transform.scale(pg.image.load(path.join(dir_images, 'background.jpeg')),
                                                   (screen.get_width(), screen.get_height()))
        State._font_size_base = round(screen.get_height() / 25)
        State._class_is_initialised = True

    @staticmethod
    def get_background_img():
        if not State._class_is_initialised:
            raise ValueError(f"Class is not initialized. Call {__class__.__name__}.initialise() first.")
        return State._background_img

    @staticmethod
    def get_font_size_base():
        if not State._class_is_initialised:
            raise ValueError(f"Class is not initialized. Call {__class__.__name__}.initialise() first.")
        return State._font_size_base

    def __init__(self):
        if not State._class_is_initialised:
            raise ValueError(f"Class is not initialized. Call {__class__.__name__}.initialise() first.")

    def handle_events(self, events, frame_time):
        pass

    def render(self):
        pass
