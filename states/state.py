import pygame as pg
from os import path
from enum import Enum

from utils.paths import dir_images, dir_sound

pg.init()


class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class State:
    def __init__(self, screen_: pg.Surface):
        self.screen = screen_
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

    def handle_events(self, events, frame_time):
        raise NotImplementedError("Subclass must implement abstract method")

    def render(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_frame_rate(self) -> int:
        # Classes derived from State class are supposed to overwrite this method to return a reasonable frame rate
        return 60
