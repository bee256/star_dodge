import pygame as pg
import time
from os import path

from states.state import State, Difficulty
from elements.ship import Ship
from elements.star import Star
from elements.explosion import Explosion
from utils.colors import LIGHT_BLUE, DARK_RED
from utils.paths import dir_sound, dir_fonts


pg.init()
pg.font.init()

SCREEN: pg.Surface
TIME_FONT: pg.font.Font
LOST_FONT: pg.font.Font
LOST_TEXT: pg.Surface

SOUND_CRASH: pg.mixer.Sound
SOUND_HIT: pg.mixer.Sound


class GameState(State):
    _class_is_initialised = False
    _background_img: pg.Surface
    _game_over_wait_time_secs = 3

    @staticmethod
    def initialise(screen: pg.Surface):
        if GameState._class_is_initialised:
            return

        State.initialise(screen)
        _background_img = State.get_background_img()
        font_size_base = State.get_font_size_base()
        global SCREEN, TIME_FONT, LOST_FONT, LOST_TEXT, SOUND_CRASH, SOUND_HIT
        SCREEN = screen
        TIME_FONT = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), font_size_base)
        LOST_FONT = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), font_size_base * 2)
        LOST_TEXT = LOST_FONT.render("RAUMSCHIFF KAPUTT!", 1, DARK_RED)
        SOUND_CRASH = pg.mixer.Sound(path.join(dir_sound, 'rubble_crash.wav'))
        SOUND_HIT = pg.mixer.Sound(path.join(dir_sound, 'metal_trash_can_filled_2.wav'))
        GameState._class_is_initialised = True

    def __init__(self, menu_state: State):
        if not GameState._class_is_initialised:
            raise ValueError(f"Class is not initialized. Call {__class__.__name__}.initialise() first.")

        super().__init__()
        self.menu_state = menu_state
        self.star_create_timer = 0
        self.start_time = time.time()
        self.star_add_increment = 1500
        self.start_time = time.time()
        self.ship = Ship(SCREEN)
        self.ship_draw_in_color = True  # to let ship blink
        self.ship_toggle_time = 0.5
        self.ship_blink_time = time.time() + self.ship_toggle_time  # Time when ship should toggle color
        self.hits = 0
        self.game_over_start = 0
        self.stars = []
        Star.initialise(SCREEN)
        Explosion.initialise(SCREEN)
        self.explosion_group = pg.sprite.Group()
        if State.play_music:
            pg.mixer.music.play(loops=-1)
        self.pause_start = 0
        if State.difficulty == Difficulty.EASY:
            self.stars_create_per_increment = 3
        elif State.difficulty == Difficulty.HARD:
            self.stars_create_per_increment = 5
        else:  # Normal state
            self.stars_create_per_increment = 4

    def handle_events(self, events, frame_time):
        if self.game_over_start:
            time_since_game_over = time.time() - self.game_over_start
            if time_since_game_over > GameState._game_over_wait_time_secs:
                # return to MenuState but no current running game as it is over
                self.menu_state.set_running_game(None)
                return self.menu_state
            else:
                return None     # keep game going until end of game over animation and music fade out

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.ship.move_left()
        if keys[pg.K_RIGHT]:
            self.ship.move_right()
        if keys[pg.K_ESCAPE] or keys[pg.K_SPACE]:
            pg.mixer.music.pause()
            self.pause_start = time.time()
            # return in pause mode
            self.menu_state.set_running_game(self)
            return self.menu_state

        self.star_create_timer += frame_time

        # game logic: every star_add_increment we create a bunch of stars
        if self.star_create_timer > self.star_add_increment:
            for _ in range(self.stars_create_per_increment):
                star = Star()
                self.stars.append(star)

            # here we decrease star_add_increment, so that starts get created faster and faster, but not faster than a threshold
            self.star_add_increment = max(150, self.star_add_increment - 50)
            self.star_create_timer = 0

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
                if State.play_sound:
                    pg.mixer.Sound.play(SOUND_HIT)
                return None

            # hits is > as exit threshold → exit mode of game state
            self.game_over_start = time.time()
            if State.play_sound:
                pg.mixer.Sound.play(SOUND_CRASH)
            # make remaining music 250 ms less than wait time when game is over
            pg.mixer.music.fadeout(GameState._game_over_wait_time_secs * 1000 - 250)
            return None

    def render(self):
        elapsed_time = time.time() - self.start_time
        if self.pause_start:
            self.start_time += time.time() - self.pause_start
            self.pause_start = 0

        SCREEN.blit(GameState._background_img, (0, 0))
        # self.ship.draw_all_ships_for_test()

        if time.time() > self.ship_blink_time:
            self.ship_draw_in_color = not self.ship_draw_in_color
            self.ship_blink_time = time.time() + self.ship_toggle_time

        if self.ship_draw_in_color:
            self.ship.draw(self.get_color_by_hits())
        else:
            self.ship.draw('green')

        for star in self.stars:
            star.draw()

        self.explosion_group.draw(SCREEN)
        self.explosion_group.update()

        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_text = TIME_FONT.render(f"TIME: {minutes:02d}:{seconds:02d}", 1, pg.Color(LIGHT_BLUE))
        SCREEN.blit(time_text, (30, 10))
        hits_text = TIME_FONT.render(f"HITS: {self.hits}", 1, self.get_color_by_hits())
        SCREEN.blit(hits_text, (SCREEN.get_width() - hits_text.get_width() - 30, 10))

        if self.game_over_start:
            SCREEN.blit(LOST_TEXT, (
                SCREEN.get_width() / 2 - LOST_TEXT.get_width() / 2, SCREEN.get_height() / 2 - LOST_TEXT.get_height() / 2))

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
