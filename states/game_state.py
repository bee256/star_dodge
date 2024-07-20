import pygame as pg
import time
import asyncio
from os import path
import csv
from datetime import datetime

from .state import State
from .stage_manager import StageManager
from .helper import Message
from elements.ship import Ship
from elements.star import Star
from elements.explosion import Explosion
from utils.settings import Settings, Difficulty
from utils.colors import LIGHT_BLUE, DARK_RED, WHITE, LIGHT_GRAY
from utils.paths import dir_sound, dir_fonts, get_highscore_path, get_data_dir, sanitize_filename
from utils.config import Config

screen: pg.Surface
settings: Settings

GAME_OVER_WAIT_TIME_SECS = 3


class GameState(State):
    def __init__(self, menu_state: State):
        super().__init__()
        self.menu_state = menu_state

        global screen, settings
        settings = Settings()
        screen = settings.screen

        self.time_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), settings.font_size_base)
        self.lost_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), settings.font_size_base * 2)
        self.info_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), round(settings.font_size_base * 0.6))
        self.lost_text = self.lost_font.render("RAUMSCHIFF KAPUTT!", 1, DARK_RED)
        immortal_text = self.lost_font.render("IMMORTAL MODE", 1, WHITE)
        self.instructions = Message("Avoid the stars!", "Left/Right arrow keys to move the ship",
                                    "Escape or Space key to pause the game")
        self.instructions_alpha = 255
        self.immortal_text = pg.Surface((immortal_text.get_width(), immortal_text.get_height()), pg.SRCALPHA)
        self.immortal_text.blit(immortal_text, (0, 0))
        self.immortal_text.set_alpha(32)  # Set the transparency level (0 is fully transparent, 255 is fully opaque)

        self.sound_crash = pg.mixer.Sound(path.join(dir_sound, 'rubble_crash.wav'))
        self.sound_hit = pg.mixer.Sound(path.join(dir_sound, 'metal_trash_can_filled_2.wav'))

        self.stage_manager = StageManager()
        self.start_time = time.time()
        self.ship = Ship(screen)
        self.ship_draw_in_color = True  # to let ship blink
        self.ship_toggle_time = 0.5
        self.ship_blink_time = time.time() + self.ship_toggle_time  # Time when ship should toggle color
        self.star_count_time = 0
        self.stars_on_screen_by_time = []
        self.hits = 0
        self.game_over_start = 0
        self.stars = []
        self.highscores = []  # Neue Liste für Highscores
        self.elapsed_time = 0.0
        self.submit_score_rc = 0
        self.submit_score_message = None
        Star.initialise(screen)
        Explosion.initialise(screen)
        self.explosion_group = pg.sprite.Group()
        if settings.play_music:
            pg.mixer.music.play(loops=-1)
        self.pause_start = 0
        if settings.difficulty == Difficulty.EASY:
            self.stars_create_per_increment = 3
        elif settings.difficulty == Difficulty.HARD:
            self.stars_create_per_increment = 5
        else:  # Normal state
            self.stars_create_per_increment = 4

        config = Config()
        self.arg_store_time_num_stars_csv = config.get_arg('store_time_num_stars_csv')

    def handle_events(self, events, frame_time):
        if self.game_over_start:
            time_since_game_over = time.time() - self.game_over_start
            if time_since_game_over > GAME_OVER_WAIT_TIME_SECS:
                # return to MenuState but no current running game as it is over
                self.menu_state.set_running_game(None)
                return self.menu_state
            else:
                return None  # keep game going until end of game over animation and music fade out

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.ship.move_left()
        if keys[pg.K_RIGHT]:
            self.ship.move_right()
        if keys[pg.K_ESCAPE] or keys[pg.K_SPACE]:
            pg.mixer.music.pause()
            self.pause_start = time.time()
            # write csv file in pause mode as well, so we can analyze as well in immortal mode
            if self.arg_store_time_num_stars_csv:
                self.write_stars_by_time()
            # return in pause mode
            self.menu_state.set_running_game(self)
            return self.menu_state
        if keys[pg.K_s] and pg.key.get_mods() & pg.KMOD_META:
            formatted_date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = sanitize_filename(f"screenshot_{settings.player_name}_{formatted_date_time}.png")
            screenshot_filename = path.join(get_data_dir(), screenshot_filename)
            pg.image.save(screen, screenshot_filename)
            print(f"Screenshot saved as {screenshot_filename}")

        if self.pause_start:
            self.start_time += time.time() - self.pause_start
            self.pause_start = 0
        self.elapsed_time = time.time() - self.start_time

        self.stage_manager.handle_stages(self.elapsed_time)
        # game logic: every star_add_increment we create a bunch of stars
        if self.stage_manager.stars_to_be_created(self.elapsed_time):
            for _ in range(self.stars_create_per_increment):
                star = Star()
                self.stars.append(star)

        is_hit = False
        for star in self.stars.copy():
            star.move()
            if star.is_off_screen():
                self.stars.remove(star)
            elif star.is_near_ship(self.ship):
                if star.collides_with_ship(self.ship):
                    self.explosion_group.add(Explosion(star.star_rect.x, star.star_rect.y))
                    self.stars.remove(star)
                    is_hit = True
                    break

        if is_hit:
            if not settings.immortal_mode:
                self.hits += 1
            if self.hits == 2:
                self.ship_toggle_time = 0.25
            if self.hits == 3:
                self.ship_toggle_time = 0.125
            if self.hits < 3:
                if settings.play_sound:
                    pg.mixer.Sound.play(self.sound_hit)
                return None

            # hits is > as exit threshold → exit mode of game state
            self.game_over_start = time.time()
            if settings.verbose:
                print(f"Game over for player {settings.player_name} with a score of {self.elapsed_time:.2f}")
            if settings.play_sound:
                pg.mixer.Sound.play(self.sound_crash)
            # make remaining music 100 ms less than wait time when game is over
            pg.mixer.music.fadeout(GAME_OVER_WAIT_TIME_SECS * 1000 - 100)
            if self.arg_store_time_num_stars_csv:
                self.write_stars_by_time()
            self.save_highscore()
            if settings.score_server_host:
                self.submit_score_rc = 0
                self.submit_score_message = f"Submitting your score {self.elapsed_time:.2f} to score server"
                # print("Now calling asyncio.create_task(settings.submit_score())")
                # start = time.time()
                asyncio.create_task(settings.submit_score(self.elapsed_time, self.on_score_submitted))
                # duration = (time.time() - start) * 1000
                # print(f"Call of asyncio.create_task took {duration} milliseconds")
            return None

    def render(self):
        screen.blit(settings.background_img, (0, 0))
        # self.ship.draw_all_ships_for_test()
        if self.elapsed_time <= 3.0:
            self.instructions.draw()
        elif self.instructions_alpha > 0:
            self.instructions_alpha -= 2
            self.instructions.set_alpha(self.instructions_alpha)
            self.instructions.draw()

        if time.time() > self.ship_blink_time:
            self.ship_draw_in_color = not self.ship_draw_in_color
            self.ship_blink_time = time.time() + self.ship_toggle_time

        if self.ship_draw_in_color:
            self.ship.draw(self.get_color_by_hits())
        else:
            self.ship.draw('green')

        if self.arg_store_time_num_stars_csv:
            if self.elapsed_time >= self.star_count_time:
                self.stars_on_screen_by_time.append((self.elapsed_time, len(self.stars),
                                                     self.stage_manager.current_stage + 1,
                                                     self.stage_manager.get_current_create_duration()))
                self.star_count_time = self.elapsed_time + 1

        for star in self.stars:
            star.draw()

        self.explosion_group.draw(screen)
        self.explosion_group.update()

        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        time_text = self.time_font.render(f"TIME: {minutes:02d}:{seconds:02d}", 1, pg.Color(LIGHT_BLUE))
        time_and_hits_text_offset = time_text.get_height() / 1.5
        screen.blit(time_text, (time_and_hits_text_offset, time_and_hits_text_offset))
        stage_text = self.time_font.render(self.stage_manager.get_stage_str(), 1, pg.Color(LIGHT_GRAY))
        screen.blit(stage_text, (screen.get_width() / 2 - stage_text.get_width() / 2, time_and_hits_text_offset))
        hits_text = self.time_font.render(f"HITS: {self.hits}", 1, self.get_color_by_hits())
        screen.blit(hits_text, (screen.get_width() - hits_text.get_width() - time_and_hits_text_offset, time_and_hits_text_offset))

        self.draw_player_name()

        if settings.immortal_mode:
            screen.blit(self.immortal_text, (screen.get_width() / 2 - self.immortal_text.get_width() / 2, screen.get_height() / 2 - self.immortal_text.get_height() / 2))

        if self.game_over_start:
            screen.blit(self.lost_text, (screen.get_width() / 2 - self.lost_text.get_width() / 2, screen.get_height() / 2 - self.lost_text.get_height() / 2))
            # if submit_score_message is set it means that the server score host config option has been used
            # → report a message on screen if the submit action was successful.
            if self.submit_score_message:
                color = WHITE
                if self.submit_score_rc != 0:
                    color = DARK_RED
                info_text = self.info_font.render(self.submit_score_message, True, color)
                if self.submit_score_rc == 0:
                    info_text_alpha = pg.Surface((info_text.get_width(), info_text.get_height()), pg.SRCALPHA)
                    info_text_alpha.blit(info_text, (0, 0))
                    info_text_alpha.set_alpha(64)  # Set the transparency level (0 is fully transparent, 255 is fully opaque)
                    screen.blit(info_text_alpha, (info_text.get_height(), screen.get_height() - info_text.get_height() * 2))
                else:
                    # In case of an error we draw without alpha
                    screen.blit(info_text, (info_text.get_height(), screen.get_height() - info_text.get_height() * 2))

    def draw_player_name(self):
        if self.game_over_start and self.submit_score_message:
            return  # do not write the player anymore, as the submit core message will be written
        # TODO: move rendering of player to __init__ as it stays constant during a game
        info_text = self.info_font.render(f"Player: {settings.player_name}", True, WHITE)
        # Create a transparent surface for the text
        info_text_alpha = pg.Surface((info_text.get_width(), info_text.get_height()), pg.SRCALPHA)
        info_text_alpha.blit(info_text, (0, 0))
        info_text_alpha.set_alpha(64)  # Set the transparency level (0 is fully transparent, 255 is fully opaque)
        screen.blit(info_text_alpha, (info_text.get_height(), screen.get_height() - info_text.get_height() * 2))

    def get_frame_rate(self) -> int:
        return 60

    def get_color_by_hits(self):
        color = 'green'
        if self.hits == 1:
            color = 'yellow'
        elif self.hits == 2:
            color = 'orange'
        elif self.hits >= 3:
            color = 'red'
        return color

    def write_stars_by_time(self):
        # Array of tuples
        # Specify the CSV file name
        filename = 'num_stars_by_time.csv'

        # Writing to the CSV file
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Optionally write a header
            writer.writerow(['Time', '# Stars', 'Stage', 'Create duration'])
            # Write data
            for row in self.stars_on_screen_by_time:
                writer.writerow(row)

        print(f'Data successfully written to {filename}')

    def save_highscore(self):
        # Highscore als Tuple (Spielername, Zeit, Datum) speichern
        highscore = (settings.player_name, self.elapsed_time, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.highscores.append(highscore)
        # Highscore in eine CSV-Datei schreiben
        with open(get_highscore_path(), mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(highscore)
        print(f'Highscore gespeichert: {highscore}')

    def on_score_submitted(self, result):
        if settings.verbose:
            print(f"Now in on_score_submitted() with result: {result}")
        self.submit_score_rc = result['rc']
        self.submit_score_message = result['message']
