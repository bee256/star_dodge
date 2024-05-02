import pygame as pg
from os import path
from enum import Enum

pg.init()
pg.mixer.music.load(path.join('assets', 'sound', 'planetary_paths.mp3'), 'planet_paths')


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

    difficulty: Difficulty
    difficulty = Difficulty.NORMAL

    @staticmethod
    def initialise(screen: pg.Surface):
        if State._class_is_initialised:
            return

        State._background_img = pg.transform.scale(pg.image.load(path.join('assets', 'images', 'background.jpeg')),
                                                   (screen.get_width(), screen.get_height()))
        State._font_size_base = int(screen.get_height() / 25)
        State._class_is_initialised = True

    @staticmethod
    def get_background_img():
        if not State._class_is_initialised:
            raise ValueError("Class is not initialized. Call State.initialise() first.")
        return State._background_img

    @staticmethod
    def get_font_size_base():
        if not State._class_is_initialised:
            raise ValueError("Class is not initialized. Call State.initialise() first.")
        return State._font_size_base

    def __init__(self):
        if not State._class_is_initialised:
            raise ValueError("Class is not initialized. Call State.initialise() first.")

    def handle_events(self, events, frame_time):
        pass

    def render(self):
        pass
