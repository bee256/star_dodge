import pygame as pg
from os import path
from typing import List

from states.state import State, Difficulty
from states.game_state import GameState
from states.quit_state import QuitState
from colors import LIGHT_BLUE, GRAY

pg.init()
pg.font.init()

MENU_SOUND_MOVE = pg.mixer.Sound(path.join('assets', 'sound', 'menu-move.wav'))
MENU_SOUND_SELECT = pg.mixer.Sound(path.join('assets', 'sound', 'menu-select.wav'))

SCREEN: pg.Surface


class MenuState(State):
    _class_is_initialised = False
    _background_img: pg.Surface
    menu_options = ['Play Game', 'Level: Normal', 'Sound: on', 'Music: on', 'Exit']
    _menu_font: pg.font.Font
    _menu_title_font: pg.font.Font
    _menu_title: pg.Surface

    @staticmethod
    def initialise(screen: pg.Surface):
        if MenuState._class_is_initialised:
            return

        State.initialise(screen)
        GameState.initialise(screen)
        MenuState._background_img = State.get_background_img()
        font_size_base = State.get_font_size_base()

        global SCREEN
        SCREEN = screen
        MenuState._menu_font = pg.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), font_size_base)
        MenuState._menu_title_font = pg.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), font_size_base * 2)
        MenuState._menu_title = MenuState._menu_title_font.render("Star Dodge", 1, LIGHT_BLUE)

        MenuState._class_is_initialised = True

    def __init__(self):
        super().__init__()
        self.running_game = None
        self.current_option = 0

    def set_running_game(self, running_game):
        self.running_game = running_game
        self.current_option = 0
        if running_game:
            MenuState.menu_options[0] = 'Resume Game'
            if not MenuState.menu_options[1] == 'New Game':
                MenuState.menu_options.insert(1, 'New Game')
        elif MenuState.menu_options[0] == 'Resume Game':
            MenuState.menu_options[0] = 'Play Game'
            MenuState.menu_options.remove('New Game')
        return self

    def handle_events(self, events: List[pg.event.Event], frame_time):
        for event in events:
            if not event.type == pg.KEYDOWN:
                continue
            if event.key == pg.K_UP:
                self.current_option = (self.current_option - 1) % len(MenuState.menu_options)
                if State.play_sound:
                    pg.mixer.Sound.play(MENU_SOUND_MOVE)
            elif event.key == pg.K_DOWN:
                self.current_option = (self.current_option + 1) % len(MenuState.menu_options)
                if State.play_sound:
                    pg.mixer.Sound.play(MENU_SOUND_MOVE)
            elif event.key == pg.K_RETURN:
                return_value = self.__handle_menu_selection(MenuState.menu_options[self.current_option])
                if State.play_sound:
                    if 'Game' not in MenuState.menu_options[self.current_option]:
                        pg.mixer.Sound.play(MENU_SOUND_SELECT)
                    elif not State.play_music:
                        pg.mixer.Sound.play(MENU_SOUND_SELECT)
                if return_value:
                    return return_value

    def __handle_menu_selection(self, selected_option):
        print(f'Option selected: {selected_option}')
        if selected_option.startswith('Level'):
            if selected_option.endswith('Easy'):
                MenuState.menu_options[self.current_option] = 'Level: Normal'
                State.difficulty = Difficulty.NORMAL
            elif selected_option.endswith('Normal'):
                MenuState.menu_options[self.current_option] = 'Level: Hard'
                State.difficulty = Difficulty.HARD
            else:
                MenuState.menu_options[self.current_option] = 'Level: Easy'
                State.difficulty = Difficulty.EASY
            return None
        elif selected_option == 'Play Game' or selected_option == 'New Game':
            return GameState(self)  # new game
        elif selected_option == 'Resume Game':
            if State.play_music:
                pg.mixer.music.unpause()
                if pg.mixer.music.get_busy() is False:
                    pg.mixer.music.play(loops=-1)
            return self.running_game
        elif selected_option == "Exit":
            return QuitState()
        elif selected_option.startswith("Music"):
            if selected_option.endswith("on"):
                MenuState.menu_options[self.current_option] = 'Music: off'
                State.play_music = False
            else:
                MenuState.menu_options[self.current_option] = 'Music: on'
                State.play_music = True
        elif selected_option.startswith("Sound"):
            if selected_option.endswith("on"):
                MenuState.menu_options[self.current_option] = 'Sound: off'
                State.play_sound = False
            else:
                MenuState.menu_options[self.current_option] = 'Sound: on'
                State.play_sound = True

    def render(self):
        SCREEN.blit(MenuState._background_img, (0, 0))
        SCREEN.blit(MenuState._menu_title, (SCREEN.get_width() / 2 - MenuState._menu_title.get_width() / 2, SCREEN.get_height() / 5))

        for i, option in enumerate(MenuState.menu_options):
            if i == self.current_option:
                label = MenuState._menu_font.render(option, True, LIGHT_BLUE)
            else:
                label = MenuState._menu_font.render(option, True, GRAY)
            width = label.get_width()
            height = label.get_height()
            pos_x = (SCREEN.get_width() / 2) - (width / 2)
            pos_y = (SCREEN.get_height() / 2) - (height / 2) + (i * height * 1.2)
            SCREEN.blit(label, (pos_x, pos_y))
