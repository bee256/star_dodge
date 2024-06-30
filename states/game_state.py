import pygame as pg
import time
from os import path
import csv

from .state import State
from elements.ship import Ship
from elements.star import Star
from elements.explosion import Explosion
from utils.settings import Settings, Difficulty
from utils.colors import LIGHT_BLUE, DARK_RED, WHITE
from utils.paths import dir_sound, dir_fonts
from utils.config import Config

screen: pg.Surface
settings: Settings

# TIME_ADD_STARS_INCREMENT_INIT is the time in milliseconds which is used to initialize the timer
# self.star_add_increment. Every self.star_add_increment milliseconds new stars will be created on the screen.
TIME_ADD_STARS_INCREMENT_INIT = 1000
# TIME_ADD_STARS_INCREMENT_MIN_TIME is the minimum time for self.star_add_increment.
# self.star_add_increment is reduced during playing time, but will never be lower than TIME_ADD_STARS_INCREMENT_MIN_TIME.
TIME_ADD_STARS_INCREMENT_MIN_TIME = 200
TIME_ADD_STARS_INCREMENT_MIN_TIME_STAGE2 = 100
# TIME_ADD_STARS_INCREMENT_TIMER_DECREASE defines the time in milliseconds, when the timer self.star_add_increment
# is reduced. This means that every TIME_ADD_STARS_INCREMENT_TIMER_DECREASE milliseconds the self.star_add_increment timer
# is reduced by TIME_ADD_STARS_INCREMENT_DECREASE milliseconds.
TIME_ADD_STARS_INCREMENT_TIMER_DECREASE = 1000
TIME_ADD_STARS_INCREMENT_DECREASE = 25
TIME_ADD_STARS_INCREMENT_DECREASE_STAGE2 = 10
# After TIME_BEGIN_STAGE2_AFTER_SECONDS seconds play time, we will make the game again harder and decrease self.star_add_increment
# even more but not below TIME_ADD_STARS_INCREMENT_MIN_TIME_STAGE2
TIME_BEGIN_STAGE2_AFTER_SECONDS = 120

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
        self.sound_crash = pg.mixer.Sound(path.join(dir_sound, 'rubble_crash.wav'))
        self.sound_hit = pg.mixer.Sound(path.join(dir_sound, 'metal_trash_can_filled_2.wav'))

        self.star_create_timer = 0
        self.star_change_increment_timer = 0
        self.start_time = time.time()
        self.star_add_increment = TIME_ADD_STARS_INCREMENT_INIT
        self.add_stars_increment_min_time = TIME_ADD_STARS_INCREMENT_MIN_TIME
        self.add_stars_increment_decrease = TIME_ADD_STARS_INCREMENT_DECREASE
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

        self.elapsed_time = time.time() - self.start_time
        if self.pause_start:
            self.start_time += time.time() - self.pause_start
            self.pause_start = 0

        if self.elapsed_time >= TIME_BEGIN_STAGE2_AFTER_SECONDS:
            self.add_stars_increment_min_time = TIME_ADD_STARS_INCREMENT_MIN_TIME_STAGE2
            self.add_stars_increment_decrease = TIME_ADD_STARS_INCREMENT_DECREASE_STAGE2

        self.star_create_timer += frame_time
        self.star_change_increment_timer += frame_time

        # game logic: every star_add_increment we create a bunch of stars
        if self.star_create_timer >= self.star_add_increment:
            for _ in range(self.stars_create_per_increment):
                star = Star()
                self.stars.append(star)
                self.star_create_timer = 0

        if self.star_change_increment_timer >= TIME_ADD_STARS_INCREMENT_TIMER_DECREASE:
            # here we decrease star_add_increment, so that stars get created faster and faster, but not faster than a threshold
            self.star_add_increment = max(self.add_stars_increment_min_time, self.star_add_increment - self.add_stars_increment_decrease)
            self.star_change_increment_timer = 0

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
            if settings.score_server_host:
                self.submit_score_rc, self.submit_score_message = settings.submit_score(self.elapsed_time)
            if settings.play_sound:
                pg.mixer.Sound.play(self.sound_crash)
            # make remaining music 100 ms less than wait time when game is over
            pg.mixer.music.fadeout(GAME_OVER_WAIT_TIME_SECS * 1000 - 100)
            if self.arg_store_time_num_stars_csv:
                self.write_stars_by_time()
            return None

    def render(self):
        screen.blit(settings.background_img, (0, 0))
        # self.ship.draw_all_ships_for_test()

        if time.time() > self.ship_blink_time:
            self.ship_draw_in_color = not self.ship_draw_in_color
            self.ship_blink_time = time.time() + self.ship_toggle_time

        if self.ship_draw_in_color:
            self.ship.draw(self.get_color_by_hits())
        else:
            self.ship.draw('green')

        if self.arg_store_time_num_stars_csv:
            if self.elapsed_time >= self.star_count_time:
                self.stars_on_screen_by_time.append((self.elapsed_time, len(self.stars)))
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
        hits_text = self.time_font.render(f"HITS: {self.hits}", 1, self.get_color_by_hits())
        screen.blit(hits_text, (screen.get_width() - hits_text.get_width() - time_and_hits_text_offset, time_and_hits_text_offset))

        if self.game_over_start:
            screen.blit(self.lost_text, (
                screen.get_width() / 2 - self.lost_text.get_width() / 2, screen.get_height() / 2 - self.lost_text.get_height() / 2))

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
            writer.writerow(['Time', '# Stars'])
            # Write data
            for row in self.stars_on_screen_by_time:
                writer.writerow(row)

        print(f'Data successfully written to {filename}')
