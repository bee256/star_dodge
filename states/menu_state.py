import pygame as pg
from os import path
from typing import List

from .menu_item import MenuItem, MenuItemType
from .set_player_state import SetPlayerState
from .state import State, Difficulty
from .game_state import GameState
from .quit_state import QuitState
from utils.colors import LIGHT_BLUE, GRAY
from utils.paths import dir_sound, dir_fonts, dir_images

pg.init()
pg.font.init()

MENU_SOUND_MOVE: pg.mixer.Sound
MENU_SOUND_SELECT: pg.mixer.Sound
SCREEN: pg.Surface


class MenuState(State):
    _class_is_initialised = False
    _background_img: pg.Surface
    _ship_img: pg.Surface
    _font_size_base: int
    _title_word1: pg.Surface
    _title_word2: pg.Surface
    _instructions_line1: pg.Surface
    _instructions_line2: pg.Surface

    @staticmethod
    def initialise(screen: pg.Surface):
        if MenuState._class_is_initialised:
            return

        State.initialise(screen)
        GameState.initialise(screen)
        SetPlayerState.initialise(screen)
        MenuState._background_img = State.get_background_img()
        MenuState._ship_img = pg.image.load(path.join(dir_images, f"space_ship3_0green.png"))
        image_aspect = MenuState._ship_img.get_height() / MenuState._ship_img.get_width()
        image_height = MenuState._font_size_base * 3
        MenuState._ship_img = pg.transform.smoothscale(MenuState._ship_img, (image_height / image_aspect, image_height))
        MenuState._font_size_base = State.get_font_size_base()
        MenuItem.initialise(screen, round(MenuState._font_size_base * 1.2))

        global SCREEN, MENU_SOUND_MOVE, MENU_SOUND_SELECT
        SCREEN = screen
        title_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), round(MenuState._font_size_base * 2.5))
        MenuState._title_word1 = title_font.render("STAR ", 1, LIGHT_BLUE)
        MenuState._title_word2 = title_font.render(" DODGE", 1, LIGHT_BLUE)
        instructions_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), round(MenuState._font_size_base * 0.6))
        MenuState._instructions_line1 = instructions_font.render("Arrow keys to move", 1, GRAY)
        MenuState._instructions_line2 = instructions_font.render("Return/Enter to select", 1, GRAY)
        MENU_SOUND_MOVE = pg.mixer.Sound(file=path.join(dir_sound, 'menu-move.wav'))
        MENU_SOUND_SELECT = pg.mixer.Sound(file=path.join(dir_sound, 'menu-select.wav'))
        MenuState._class_is_initialised = True

    def __init__(self):
        super().__init__()
        self.menu_items: {MenuItem} = {}

        # To calculate positions of column 1 and colum 2 of the menu, we first get the full width of the menu.
        # This is the width of PLAY GAME and RESUME GAME and the half of PLAY GAME size between the two first line items.
        width_of_play_game_menu_str = MenuItem.get_rendered_size_of_menu_text("PLAY GAME")[0]
        menu_width = width_of_play_game_menu_str + width_of_play_game_menu_str / 2
        width_of_resume_game_menu_str = MenuItem.get_rendered_size_of_menu_text("RESUME GAME")[0]
        menu_width += width_of_resume_game_menu_str
        # Then the x position of the menu i.e. the first column of the menu is the in the middle of the screen - menu_width / 2
        col_left_x = SCREEN.get_width() / 2 - menu_width / 2
        col_right_x = col_left_x + menu_width - width_of_resume_game_menu_str
        grid_y = SCREEN.get_height() * 0.37
        # grid_offset_y = SCREEN.get_height() / 16
        grid_offset_y = MenuState._font_size_base * 2
        self.menu_items['play'] = MenuItem('play', 'PLAY GAME', MenuItemType.SELECT, (col_left_x, grid_y), True)
        self.menu_items['resume'] = MenuItem('resume', 'RESUME GAME', MenuItemType.SELECT, (col_right_x, grid_y), False)
        grid_y += grid_offset_y
        self.menu_items['player'] = MenuItem('player', 'PLAYER: ', MenuItemType.ENTRY, (col_left_x, grid_y), True)
        self.menu_items['player'].entry_value = State.player_name
        grid_y += grid_offset_y
        self.menu_items['level'] = MenuItem('level', 'LEVEL: NORMAL', MenuItemType.SELECT, (col_left_x, grid_y), True)
        grid_y += grid_offset_y
        self.menu_items['sound'] = MenuItem('sound', 'SOUND', MenuItemType.TOGGLE, (col_left_x, grid_y), True)
        self.menu_items['music'] = MenuItem('music', 'MUSIC', MenuItemType.TOGGLE, (col_right_x, grid_y), True)
        grid_y += grid_offset_y
        self.menu_items['highscores'] = MenuItem('highscores', 'HIGHSCORES', MenuItemType.SELECT, (col_left_x, grid_y), True)
        self.menu_items['credits'] = MenuItem('credits', 'CREDITS', MenuItemType.SELECT, (col_right_x, grid_y), True)
        grid_y += grid_offset_y
        self.menu_items['exit'] = MenuItem('exit', 'EXIT', MenuItemType.SELECT, (col_left_x, grid_y), True)
        self.active_item = 'play'
        self.__set_menu_item_active(self.active_item)

        self.running_game = None

    def __set_menu_item_active(self, active_item: str):
        self.active_item = active_item
        for item in self.menu_items.keys():
            if item == active_item:
                self.menu_items[item].is_active = True
            else:
                self.menu_items[item].is_active = False

    def __move_active_item(self, direction: str):
        move_index = 1  # this is the down direction
        if direction == 'up':
            move_index = -1

        keys = list(self.menu_items.keys())
        current_index = keys.index(self.active_item)
        next_index = (current_index + move_index) % len(keys)  # Wrap around at the end or beginning
        new_active_item = keys[next_index]
        self.__set_menu_item_active(new_active_item)
        if not self.menu_items[new_active_item].is_visible:
            self.__move_active_item(direction)
            return

        if State.play_sound:
            pg.mixer.Sound.play(MENU_SOUND_MOVE)

    def set_running_game(self, running_game):
        self.running_game = running_game
        if running_game:
            self.menu_items['resume'].is_visible = True
            self.menu_items['play'].display_text = 'NEW GAME'
            self.__set_menu_item_active('resume')
        else:
            self.menu_items['resume'].is_visible = False
            self.menu_items['play'].display_text = 'PLAY GAME'
            self.__set_menu_item_active('play')

    def set_player(self):
        self.menu_items['player'].entry_value = State.player_name

    def handle_events(self, events: List[pg.event.Event], frame_time):
        for event in events:
            if not event.type == pg.KEYDOWN:
                continue
            if event.key == pg.K_UP or event.key == pg.K_LEFT:
                self.__move_active_item('up')
            elif event.key == pg.K_DOWN or event.key == pg.K_RIGHT:
                self.__move_active_item('down')
            elif event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                return_value = self.__handle_menu_selection()
                if State.play_sound:
                    if self.active_item != 'play':
                        pg.mixer.Sound.play(MENU_SOUND_SELECT)
                    elif not State.play_music:
                        pg.mixer.Sound.play(MENU_SOUND_SELECT)
                if return_value:
                    return return_value

    def __handle_menu_selection(self):
        print(f'Item selected: {self.active_item}')
        menu_item: MenuItem = self.menu_items[self.active_item]
        if self.active_item == 'level':
            if menu_item.display_text.endswith('EASY'):
                menu_item.display_text = 'LEVEL: NORMAL'
                State.difficulty = Difficulty.NORMAL
            elif menu_item.display_text.endswith('NORMAL'):
                menu_item.display_text = 'LEVEL: HARD'
                State.difficulty = Difficulty.HARD
            else:
                menu_item.display_text = 'LEVEL: EASY'
                State.difficulty = Difficulty.EASY
            return None
        elif self.active_item == 'player':
            return SetPlayerState(self)
        elif self.active_item == 'play':
            if not State.player_name:
                return SetPlayerState(self)
            return GameState(self)  # new game
        elif self.active_item == 'resume':
            if State.play_music:
                pg.mixer.music.unpause()
                if pg.mixer.music.get_busy() is False:
                    pg.mixer.music.play(loops=-1)
            return self.running_game
        elif self.active_item == 'exit':
            return QuitState()
        elif self.active_item == 'music':
            menu_item.toggle_value = not menu_item.toggle_value
            State.play_music = menu_item.toggle_value
        elif self.active_item == 'sound':
            menu_item.toggle_value = not menu_item.toggle_value
            State.play_sound = menu_item.toggle_value

    def render(self):
        SCREEN.blit(MenuState._background_img, (0, 0))
        total_size_menu_title = MenuState._title_word1.get_width() + MenuState._ship_img.get_width() + MenuState._title_word2.get_width()
        word1_pos_x = SCREEN.get_width() / 2 - total_size_menu_title / 2
        img_pos_x = word1_pos_x + MenuState._title_word1.get_width()
        word2_pos_x = img_pos_x + MenuState._ship_img.get_width()
        SCREEN.blit(MenuState._title_word1, (word1_pos_x, SCREEN.get_height() * 0.16))
        SCREEN.blit(MenuState._ship_img, (img_pos_x, SCREEN.get_height() * 0.16))
        SCREEN.blit(MenuState._title_word2, (word2_pos_x, SCREEN.get_height() * 0.16))

        # line 2 of the instructions is longer, so this one is used for the pox_x calculation
        line_height = MenuState._instructions_line1.get_height()
        instructions_pos_x = SCREEN.get_width() - MenuState._instructions_line2.get_width() - line_height
        instructions_pos_y1 = SCREEN.get_height() - 3 * line_height
        instructions_pos_y2 = SCREEN.get_height() - 2 * line_height

        SCREEN.blit(MenuState._instructions_line1, (instructions_pos_x, instructions_pos_y1))
        SCREEN.blit(MenuState._instructions_line2, (instructions_pos_x, instructions_pos_y2))

        for mi in self.menu_items.values():
            mi.draw()

    def get_frame_rate(self) -> int:
        return 20
