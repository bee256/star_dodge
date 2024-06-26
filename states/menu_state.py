import pygame as pg
from os import path
from typing import List

from .state import State
from .menu_item import MenuItem, MenuItemType
from .set_player_state import SetPlayerState
from .game_state import GameState
from .quit_state import QuitState
from utils.settings import Settings, Difficulty
from utils.colors import LIGHT_BLUE, GRAY
from utils.paths import dir_sound, dir_fonts, dir_images

screen: pg.Surface
settings: Settings


class MenuState(State):
    def __init__(self):
        super().__init__()

        global screen, settings
        settings = Settings()
        screen = settings.screen

        self._ship_img = pg.image.load(path.join(dir_images, f"space_ship3_0green.png"))
        image_aspect = self._ship_img.get_height() / self._ship_img.get_width()
        image_height = settings.font_size_base * 3
        self._ship_img = pg.transform.smoothscale(self._ship_img, (image_height / image_aspect, image_height))
        MenuItem.initialise(screen, round(settings.font_size_base * 1.2))

        title_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), round(settings.font_size_base * 2.5))
        self._title_word1 = title_font.render("STAR ", 1, LIGHT_BLUE)
        self._title_word2 = title_font.render(" DRIFT", 1, LIGHT_BLUE)
        instructions_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), round(settings.font_size_base * 0.6))
        self._instructions_line1 = instructions_font.render("Arrow keys to move", 1, GRAY)
        self._instructions_line2 = instructions_font.render("Return/Enter to select", 1, GRAY)
        self.menu_sound_move = pg.mixer.Sound(file=path.join(dir_sound, 'menu-move.wav'))
        self.menu_sound_select = pg.mixer.Sound(file=path.join(dir_sound, 'menu-select.wav'))
        MenuState._class_is_initialised = True

        self.menu_items: {MenuItem} = {}

        # To calculate positions of column 1 and colum 2 of the menu, we first get the full width of the menu.
        # This is the width of PLAY GAME and RESUME GAME and the half of PLAY GAME size between the two first line items.
        width_of_play_game_menu_str = MenuItem.get_rendered_size_of_menu_text("PLAY GAME")[0]
        menu_width = width_of_play_game_menu_str + width_of_play_game_menu_str / 2
        width_of_resume_game_menu_str = MenuItem.get_rendered_size_of_menu_text("RESUME GAME")[0]
        menu_width += width_of_resume_game_menu_str
        # Then the x position of the menu i.e. the first column of the menu is the in the middle of the screen - menu_width / 2
        col_left_x = screen.get_width() / 2 - menu_width / 2
        col_right_x = col_left_x + menu_width - width_of_resume_game_menu_str
        grid_y = screen.get_height() * 0.37
        # grid_offset_y = SCREEN.get_height() / 16
        grid_offset_y = settings.font_size_base * 2
        self.menu_items['play'] = MenuItem('play', 'PLAY GAME', MenuItemType.SELECT, (col_left_x, grid_y), True)
        self.menu_items['resume'] = MenuItem('resume', 'RESUME GAME', MenuItemType.SELECT, (col_right_x, grid_y), False)
        grid_y += grid_offset_y
        self.menu_items['player'] = MenuItem('player', 'PLAYER: ', MenuItemType.ENTRY, (col_left_x, grid_y), True)
        self.menu_items['player'].entry_value = settings.player_name
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

        if settings.play_sound:
            pg.mixer.Sound.play(self.menu_sound_move)

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
        self.menu_items['player'].entry_value = settings.player_name

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
                if settings.play_sound:
                    if self.active_item != 'play':
                        pg.mixer.Sound.play(self.menu_sound_select)
                    elif not settings.play_music:
                        pg.mixer.Sound.play(self.menu_sound_select)
                if return_value:
                    return return_value

    def __handle_menu_selection(self):
        if settings.verbose:
            print(f'Menu item selected: {self.active_item}')
        menu_item: MenuItem = self.menu_items[self.active_item]
        if self.active_item == 'level':
            if menu_item.display_text.endswith('EASY'):
                menu_item.display_text = 'LEVEL: NORMAL'
                settings.difficulty = Difficulty.NORMAL
            elif menu_item.display_text.endswith('NORMAL'):
                menu_item.display_text = 'LEVEL: HARD'
                settings.difficulty = Difficulty.HARD
            else:
                menu_item.display_text = 'LEVEL: EASY'
                settings.difficulty = Difficulty.EASY
            return None
        elif self.active_item == 'player':
            return SetPlayerState(self)
        elif self.active_item == 'play':
            if not settings.player_name:
                return SetPlayerState(self)
            return GameState(self)  # new game
        elif self.active_item == 'resume':
            if settings.play_music:
                pg.mixer.music.unpause()
                if pg.mixer.music.get_busy() is False:
                    pg.mixer.music.play(loops=-1)
            return self.running_game
        elif self.active_item == 'exit':
            return QuitState()
        elif self.active_item == 'music':
            menu_item.toggle_value = not menu_item.toggle_value
            settings.play_music = menu_item.toggle_value
        elif self.active_item == 'sound':
            menu_item.toggle_value = not menu_item.toggle_value
            settings.play_sound = menu_item.toggle_value

    def render(self):
        screen.blit(settings.background_img, (0, 0))
        total_size_menu_title = self._title_word1.get_width() + self._ship_img.get_width() + self._title_word2.get_width()
        word1_pos_x = screen.get_width() / 2 - total_size_menu_title / 2
        img_pos_x = word1_pos_x + self._title_word1.get_width()
        word2_pos_x = img_pos_x + self._ship_img.get_width()
        screen.blit(self._title_word1, (word1_pos_x, screen.get_height() * 0.16))
        screen.blit(self._ship_img, (img_pos_x, screen.get_height() * 0.16))
        screen.blit(self._title_word2, (word2_pos_x, screen.get_height() * 0.16))

        # line 2 of the instructions is longer, so this one is used for the pox_x calculation
        line_height = self._instructions_line1.get_height()
        instructions_pos_x = screen.get_width() - self._instructions_line2.get_width() - line_height
        instructions_pos_y1 = screen.get_height() - 3 * line_height
        instructions_pos_y2 = screen.get_height() - 2 * line_height

        screen.blit(self._instructions_line1, (instructions_pos_x, instructions_pos_y1))
        screen.blit(self._instructions_line2, (instructions_pos_x, instructions_pos_y2))

        for mi in self.menu_items.values():
            mi.draw()

    def get_frame_rate(self) -> int:
        return 20
