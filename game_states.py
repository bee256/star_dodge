import pygame as pg
import time
from os import path
from typing import List

from ship import Ship
from star import Star
from colors import LIGHT_BLUE, GRAY, DARK_RED

pg.init()
pg.font.init()

play_music = True
play_sound = True
MENU_SOUND_MOVE = pg.mixer.Sound(path.join('assets', 'sound', 'menu-move.wav'))
MENU_SOUND_SELECT = pg.mixer.Sound(path.join('assets', 'sound', 'menu-select.wav'))

BG_IMG: pg.Surface
FONT_SIZE_BASE: int
TIME_FONT: pg.font.Font
LOST_FONT: pg.font.Font
LOST_TEXT: pg.Surface
MENU_TEXT: pg.Surface
is_initialised = False


class State:
    def __init__(self):
        pass

    def handle_events(self, events, frame_time):
        pass

    def render(self):
        pass


class MenuState(State):
    menu_options = ['Play Game', 'Level: Normal', 'Sound: on', 'Music: on', 'Exit']

    def __init__(self, screen: pg.Surface, running_game):
        self.screen = screen

        global is_initialised, BG_IMG, FONT_SIZE_BASE, TIME_FONT, LOST_FONT, LOST_TEXT, MENU_TEXT
        if not is_initialised:
            BG_IMG = pg.transform.scale(pg.image.load(path.join('assets', 'images', 'background.jpeg')),
                                        (screen.get_width(), screen.get_height()))
            FONT_SIZE_BASE = int(screen.get_height() / 25)
            TIME_FONT = pg.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), FONT_SIZE_BASE)
            LOST_FONT = pg.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), FONT_SIZE_BASE * 2)
            LOST_TEXT = LOST_FONT.render("Raumschiff kaputt!", 1, DARK_RED)
            MENU_TEXT = LOST_FONT.render("Star Dodge", 1, LIGHT_BLUE)
            is_initialised = True

        self.running_game = running_game
        if self.running_game:
            MenuState.menu_options[0] = 'Resume Game'
            if not MenuState.menu_options[1] == 'New Game':
                MenuState.menu_options.insert(1, 'New Game')
        elif MenuState.menu_options[0] == 'Resume Game':
            MenuState.menu_options[0] = 'Play Game'
            MenuState.menu_options.remove('New Game')
        self.current_option = 0

    def handle_events(self, events: List[pg.event.Event], frame_time):
        for event in events:
            if not event.type == pg.KEYDOWN:
                continue
            if event.key == pg.K_UP:
                self.current_option = (self.current_option - 1) % len(MenuState.menu_options)
                if play_sound:
                    pg.mixer.Sound.play(MENU_SOUND_MOVE)
            elif event.key == pg.K_DOWN:
                self.current_option = (self.current_option + 1) % len(MenuState.menu_options)
                if play_sound:
                    pg.mixer.Sound.play(MENU_SOUND_MOVE)
            elif event.key == pg.K_RETURN:
                return_value = self.__handle_menu_selection(MenuState.menu_options[self.current_option])
                if play_sound:
                    if 'Game' not in MenuState.menu_options[self.current_option]:
                        pg.mixer.Sound.play(MENU_SOUND_SELECT)
                    elif not play_music:
                        pg.mixer.Sound.play(MENU_SOUND_SELECT)
                if return_value:
                    return return_value

    def __handle_menu_selection(self, selected_option):
        global play_music, play_sound
        print(f'Option selected: {selected_option}')
        if selected_option.startswith('Level'):
            if selected_option.endswith('Easy'):
                MenuState.menu_options[self.current_option] = 'Level: Normal'
            elif selected_option.endswith('Normal'):
                MenuState.menu_options[self.current_option] = 'Level: Hard'
            else:
                MenuState.menu_options[self.current_option] = 'Level: Easy'
            return None
        elif selected_option == 'Play Game' or selected_option == 'New Game':
            return GameState(self.screen)  # new game
        elif selected_option == 'Resume Game':
            if play_music:
                pg.mixer.music.unpause()
                if pg.mixer.music.get_busy() is False:
                    pg.mixer.music.play(loops=-1)
            return self.running_game
        elif selected_option == "Exit":
            return QuitState()
        elif selected_option.startswith("Music"):
            if selected_option.endswith("on"):
                MenuState.menu_options[self.current_option] = 'Music: off'
                play_music = False
            else:
                MenuState.menu_options[self.current_option] = 'Music: on'
                play_music = True
        elif selected_option.startswith("Sound"):
            if selected_option.endswith("on"):
                MenuState.menu_options[self.current_option] = 'Sound: off'
                play_sound = False
            else:
                MenuState.menu_options[self.current_option] = 'Sound: on'
                play_sound = True

    def render(self):
        self.screen.blit(BG_IMG, (0, 0))
        self.screen.blit(MENU_TEXT, (self.screen.get_width() / 2 - MENU_TEXT.get_width() / 2, self.screen.get_height() / 5))

        for i, option in enumerate(MenuState.menu_options):
            if i == self.current_option:
                label = TIME_FONT.render(option, True, LIGHT_BLUE)
            else:
                label = TIME_FONT.render(option, True, GRAY)
            width = label.get_width()
            height = label.get_height()
            pos_x = (self.screen.get_width() / 2) - (width / 2)
            pos_y = (self.screen.get_height() / 2) - (height / 2) + (i * height * 1.2)
            self.screen.blit(label, (pos_x, pos_y))


STARS_CREATE_PER_INCREMENT = 4
SOUND_CRASH = pg.mixer.Sound(path.join('assets', 'sound', 'rubble_crash.wav'))
SOUND_HIT = pg.mixer.Sound(path.join('assets', 'sound', 'metal_trash_can_filled_2.wav'))
pg.mixer.music.load(path.join('assets', 'sound', 'planetary_paths.mp3'), 'planet_paths')
HITS_MAX = 3


class GameState(State):
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.star_create_timer = 0
        self.start_time = time.time()
        self.star_add_increment = 1500
        self.start_time = time.time()
        self.ship = Ship(screen)
        self.hits = 0
        self.stars = []
        Star.initialise(screen)
        if play_music:
            pg.mixer.music.play(loops=-1)
        self.pause_start = 0

    def handle_events(self, events, frame_time):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.ship.move_left()
        if keys[pg.K_RIGHT]:
            self.ship.move_right()
        if keys[pg.K_ESCAPE]:
            pg.mixer.music.pause()
            self.pause_start = time.time()
            return MenuState(self.screen, self)

        self.star_create_timer += frame_time

        # game logic: every star_add_increment we create a bunch of stars
        if self.star_create_timer > self.star_add_increment:
            for _ in range(STARS_CREATE_PER_INCREMENT):
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
                    self.stars.remove(star)
                    is_hit = True
                    break

        if is_hit:
            self.hits += 1
            if self.hits < 3:
                if play_sound:
                    pg.mixer.Sound.play(SOUND_HIT)
                return None

            # hits is > as exit threshold → exit game
            if play_sound:
                pg.mixer.Sound.play(SOUND_CRASH)
            self.render()
            pg.display.flip()
            pg.mixer.music.fadeout(2500)
            pg.time.delay(2000)
            return MenuState(self.screen, None)

    def render(self):
        elapsed_time = time.time() - self.start_time
        if self.pause_start:
            self.start_time += time.time() - self.pause_start
            self.pause_start = 0

        self.screen.blit(BG_IMG, (0, 0))
        # self.ship.draw_all_ships_for_test()

        self.ship.draw(self.get_color_by_hits())

        for star in self.stars:
            star.draw()

        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_text = TIME_FONT.render(f"Time: {minutes:02d}:{seconds:02d}", 1, pg.Color(LIGHT_BLUE))
        self.screen.blit(time_text, (30, 10))
        hits_text = TIME_FONT.render(f"Hits: {self.hits}", 1, self.get_color_by_hits())
        self.screen.blit(hits_text, (self.screen.get_width() - hits_text.get_width() - 30, 10))

        if self.hits >= 3:
            self.screen.blit(LOST_TEXT, (
                self.screen.get_width() / 2 - LOST_TEXT.get_width() / 2, self.screen.get_height() / 2 - LOST_TEXT.get_height() / 2))

    def get_color_by_hits(self):
        color = 'green'
        if self.hits == 1:
            color = 'yellow'
        elif self.hits == 2:
            color = 'orange'
        elif self.hits >= 3:
            color = 'red'
        return color


class QuitState(State):
    def __init__(self):
        pass
