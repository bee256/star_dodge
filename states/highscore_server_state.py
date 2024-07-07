import asyncio
import sys
import aiohttp
import pygame as pg
from os import path
import time
from typing import List

from states.state import State
from states.helper import Instructions
from utils.colors import LIGHT_BLUE, WHITE, LIGHT_GRAY
from utils.paths import dir_fonts, dir_sound
from utils.settings import Settings

settings: Settings
screen: pg.Surface


class HighscoreServerState(State):
    def __init__(self, menu_state: State):
        self.menu_state = menu_state

        global screen, settings
        settings = Settings()
        screen = settings.screen

        self.sound_new_highscore = pg.mixer.Sound(path.join(dir_sound, 'winning-218995.mp3'))
        self.sound_new_score = pg.mixer.Sound(path.join(dir_sound, 'success-1-6297.mp3'))

        self._list_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), round(settings.font_size_base * 1.2))
        self._list_font_small = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), round(settings.font_size_base * 0.9))
        self._title_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), settings.font_size_base * 2)
        self._title = self._title_font.render("HIGHSCORES", 1, LIGHT_BLUE)
        self._instructions = Instructions("Escape key to return to main menu")
        self._last_query_time = 0
        self._scores = []
        self._previous_scores = None
        self._new_scores = []
        half_screen_width = screen.get_width() / 2
        col_width = half_screen_width / 20.0
        self.x_rank = round(2.5 * col_width)
        self.x_player = round(3.25 * col_width)
        self.x_score = round(17 * col_width)

    def handle_events(self, events: List[pg.event.Event], frame_time):
        # poll the highscores every 5 seconds
        if time.time() - self._last_query_time >= 5:
            asyncio.create_task(self.poll_high_score_server())
            self._last_query_time = time.time()

        for event in events:
            if not event.type == pg.KEYDOWN:
                continue
            if event.key == pg.K_ESCAPE:
                return self.menu_state

    def render(self):
        screen.blit(settings.background_img, (0, 0))
        title_x = screen.get_width() / 2 - self._title.get_width() / 2
        title_y = screen.get_height() / 10
        screen.blit(self._title, (title_x, title_y))

        y_base = title_y + self._title.get_height() + screen.get_height() / 17
        pg.draw.line(screen, LIGHT_GRAY, (screen.get_width() / 2, y_base), (screen.get_width() / 2, screen.get_height() - screen.get_height() / 9.5), 3)

        # draw the first 10 scores on the left side of the screen
        self.draw_scores(0, y_base, self._scores[:10])
        # draw the 2nd 10 scores on the right side of the screen
        self.draw_scores(screen.get_width() / 2, y_base, self._scores[10:20], 10)

        self._instructions.draw()

    def draw_scores(self, x_base, y_pos, scores_list, rank_offset=0):
        x_rank = x_base + self.x_rank
        x_player = x_base + self.x_player
        x_score = x_base + self.x_score

        for num, score in enumerate(scores_list):
            rank = self._list_font.render(f"{num + 1 + rank_offset}", 1, LIGHT_BLUE)
            screen.blit(rank, (x_rank - rank.get_width(), y_pos))
            player = self._list_font.render(score['name'], 1, LIGHT_BLUE)
            screen.blit(player, (x_player, y_pos))
            score_text = f"{score['score']:.2f}"
            score_left, score_right = score_text.split('.')
            comma = self._list_font.render(',', 1, LIGHT_BLUE)
            screen.blit(comma, (x_score, y_pos))
            score_left = self._list_font.render(score_left, 1, LIGHT_BLUE)
            screen.blit(score_left, (x_score - score_left.get_width(), y_pos))
            score_right = self._list_font_small.render(score_right, 1, LIGHT_BLUE)
            y_pos_for_decimal = y_pos + score_right.get_height() * 0.24
            screen.blit(score_right, (x_score + comma.get_width(), y_pos_for_decimal))
            y_pos += rank.get_height()

    def get_frame_rate(self) -> int:
        return 20

    async def poll_high_score_server(self, callback=None, num_recs: int = 20):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                        f'http://{settings.score_server_host}:{settings.score_server_port}/get_scores?n={num_recs}') as response:
                    response.raise_for_status()
                    self._scores = await response.json()
                    message = "Successfully queried scores from server"
                    if settings.verbose:
                        print(f"{message} http://{settings.score_server_host}:{settings.score_server_port}: {self._scores}")
                        print(self._scores)
                    if callback is not None:
                        callback()

            except Exception as err:
                message = f"Could not get scores from server: {err}"
                print(message, file=sys.stderr)
