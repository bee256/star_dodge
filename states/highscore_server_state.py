import asyncio
import sys
import aiohttp
import pygame as pg
from os import path
import time
from typing import List

from states.state import State
from states.helper import Message
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
        self._instructions = Message("Escape key to return to main menu")
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
            asyncio.create_task(self.poll_high_score_server(self.on_new_results))
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
            color = LIGHT_BLUE
            if self._new_scores:
                if score in self._new_scores:
                    color = WHITE
            rank = self._list_font.render(f"{num + 1 + rank_offset}", 1, color)
            screen.blit(rank, (x_rank - rank.get_width(), y_pos))
            score_text = f"{score['score']:.2f}"
            score_left, score_right = score_text.split('.')
            comma = self._list_font.render(',', 1, color)
            screen.blit(comma, (x_score, y_pos))
            score_left = self._list_font.render(score_left, 1, color)
            screen.blit(score_left, (x_score - score_left.get_width(), y_pos))
            score_right = self._list_font_small.render(score_right, 1, color)

            # Make sure long player names do not overwrite the score. Apply a nice fade out effect if too long.
            player = self._list_font.render(score['name'], 1, color)
            # Exact size of the player surface is the x_score - x_player - score_left.get_width()
            # I subtract player.get_height() / 3 more to make sure that even the faded out text is not going until exactly the score
            player_surface = pg.Surface((x_score - x_player - score_left.get_width() - player.get_height() / 3, player.get_height()), pg.SRCALPHA)
            player_surface.blit(player, (0, 0))
            fade_width = round(player_surface.get_width() * 0.2)   # Fadeout area is 20% of total width
            for i in range(1, fade_width+1):
                alpha = int(255 * (1 - (i / fade_width)))
                fade_surface = pg.Surface((1, player_surface.get_height()), pg.SRCALPHA)
                fade_surface.fill((255, 255, 255, alpha))  # Fill with white with varying alpha
                player_surface.blit(fade_surface, (player_surface.get_width() - fade_width + i, 0), special_flags=pg.BLEND_RGBA_MIN)
            screen.blit(player_surface, (x_player, y_pos))

            y_pos_for_decimal = y_pos + score_right.get_height() * 0.24
            screen.blit(score_right, (x_score + comma.get_width(), y_pos_for_decimal))
            y_pos += rank.get_height()

    def on_new_results(self):
        # new results just came in, let us look for the difference to previous results
        if self._previous_scores is None:
            self._previous_scores = self._scores
            return

        # We have new results and previous results → lets compare and figure out the new ones
        self._new_scores = []

        play_new_highscore = False
        play_new_scores = False
        for num, item in enumerate(self._scores):
            if item not in self._previous_scores:
                self._new_scores.append(item)
                if num == 0:
                    play_new_highscore = True
                else:
                    play_new_scores = True

        if play_new_highscore:
            pg.mixer.Sound.play(self.sound_new_highscore)
        elif play_new_scores:
            pg.mixer.Sound.play(self.sound_new_score)

        self._previous_scores = self._scores

        if settings.verbose:
            print(f"In on_new_results: {self._new_scores}")

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
