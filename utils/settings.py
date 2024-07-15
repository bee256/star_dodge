import sys
import socket
import aiohttp
import platform
import pygame as pg
from os import path
from enum import Enum

from utils.config import Config
from utils.paths import dir_images, dir_sound


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
        self.immortal_mode = False

        pg.mixer.music.load(path.join(dir_sound, 'planetary_paths.mp3'), 'planet_paths')
        self.background_img = pg.transform.scale(pg.image.load(path.join(dir_images, 'background.jpeg')),
                                                 (self.screen.get_width(), self.screen.get_height()))
        self.font_size_base = round(self.screen.get_height() / 25)
        config = Config()
        self.verbose = config.get_arg('verbose')
        self.score_server_host = config.get_arg('score_server_host')
        self.score_server_port = config.get_arg('score_server_port')

    async def ping_score_server(self, callback):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f'http://{self.score_server_host}:{self.score_server_port}/ping') as response:
                    response.raise_for_status()
                    message = f"Successfully pinged score server {self.score_server_host}"
                    if self.verbose:
                        print(f"{message} at http://{self.score_server_host}:{self.score_server_port}")
                    callback({'rc': 0, 'message': message})

            except Exception as err:
                message = f"Could not ping score server {self.score_server_host}"
                print(f"{message} at http://{self.score_server_host}:{self.score_server_port}", file=sys.stderr)
                callback({'rc': 1, 'message': message})

    async def submit_score(self, score, callback):
        if self.score_server_host is None:
            message = "Cannot submit score since server host is not defined"
            print(message, file=sys.stderr)
            callback({'rc': 1, 'message': message})
            return

        async with aiohttp.ClientSession() as session:
            try:
                computer_name = socket.gethostname()
                os_info = platform.system() + " " + platform.release()
                data = {
                    'name': self.player_name,
                    'score': score,
                    'nickname': None,
                    'email': None,
                    'computer_name': computer_name,
                    'os': os_info,
                    'screen_width': self.screen.get_width(),
                    'screen_height': self.screen.get_height()
                }

                async with session.post(f'http://{self.score_server_host}:{self.score_server_port}/submit_score', json=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    message = f"Successfully submitted score {score:.2f} of player {self.player_name} to server"
                    if self.verbose:
                        print(f"{message} http://{self.score_server_host}:{self.score_server_port}: {result}")
                    callback({'rc': 0, 'message': message})

            except Exception as err:
                message = f"Could not submit score {score:.2f} of player {self.player_name} to server: {err}"
                print(message, file=sys.stderr)
                callback({'rc': 1, 'message': message})
