import pygame as pg
from os import path
from typing import List
import time
import asyncio

from .state import State
from .helper import Message
from .menu_item import MenuItem, MenuItemType
from .set_player_state import SetPlayerState
from .set_immortal_mode import SetImmortalMode
from .game_state import GameState
from .quit_state import QuitState
from .credits_state import CreditsState
from .new_frame_rate_state import NewFrameRateState
from .highscore_state import HighscoreState
from .highscore_server_state import HighscoreServerState
from utils.settings import Settings, Difficulty
from utils.colors import LIGHT_BLUE, DARK_RED, WHITE
from utils.paths import dir_sound, dir_fonts, dir_images
from elements.star import Star

screen: pg.Surface
settings: Settings


class MenuState(State):
    def __init__(self):
        super().__init__()

        global screen, settings
        settings = Settings()
        screen = settings.screen

        # create a screen alpha which we use to draw in during game start animation to fade out menu
        self.screen_alpha = pg.Surface((screen.get_width(), screen.get_height()), pg.SRCALPHA)

        # Ping the server host and display the result during start of the menu
        self.ping_score_server_rc = None
        self.ping_score_server_message = None
        self.message_display = None
        self.menu_msg_time = 0
        if settings.score_server_host:
            asyncio.create_task(settings.ping_score_server(self.on_score_server_ping))

        # Create a 2nd screen with alpha to draw the stars with transparency
        self.screen_alpha_stars = pg.Surface((screen.get_width(), screen.get_height()), pg.SRCALPHA)
        self.screen_alpha_stars.set_alpha(64)

        self._ship_img_with_fire = pg.image.load(path.join(dir_images, f"space_ship3_0green.png"))
        image_aspect = self._ship_img_with_fire.get_height() / self._ship_img_with_fire.get_width()
        image_height = settings.font_size_base * 3
        self._ship_img_with_fire = pg.transform.smoothscale(self._ship_img_with_fire, (image_height / image_aspect, image_height))
        self._ship_img_no_fire = pg.image.load(path.join(dir_images, f"space_ship3_no_fire.png"))
        self._ship_img_no_fire = pg.transform.smoothscale(self._ship_img_no_fire, (image_height / image_aspect, image_height))

        MenuItem.initialise(screen, round(settings.font_size_base * 1.2))

        title_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), round(settings.font_size_base * 2.5))
        self._title_word1 = title_font.render("STAR ", 1, LIGHT_BLUE)
        self._title_word2 = title_font.render(" DODGE", 1, LIGHT_BLUE)
        self._title_y = screen.get_height() * 0.16
        self._instructions = Message("Arrow keys to move", "Return/Enter to select")
        self.menu_sound_move = pg.mixer.Sound(file=path.join(dir_sound, 'menu-move.wav'))
        self.menu_sound_select = pg.mixer.Sound(file=path.join(dir_sound, 'menu-select.wav'))

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
        self.menu_items['immortal_off'] = MenuItem('immortal_off', 'IMMORTAL OFF', MenuItemType.SELECT, (col_right_x, grid_y), False)
        self.active_item = 'play'
        self.__set_menu_item_active(self.active_item)

        self.running_game = None
        self.last_keydown_events = []
        self.game_start_animation = False
        self.gsa_sound_launch = pg.mixer.Sound(file=path.join(dir_sound, 'launch-85216.wav'))
        self.gsa_sound_launch.set_volume(0.4)
        self.new_game = None
        self.gsa_frames = 30
        self.gsa_distance = 0
        self.gsa_acceleration = 0
        self.gsa_frame_count = 0
        self.gsa_speed = 0
        self.gsa_ship_y_init = self._title_y * 1.12
        self.gsa_ship_y = self.gsa_ship_y_init

        # Initialize stars for background
        self.stars = []
        self.star_timer = 0
        Star.initialise(screen)

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

    def set_immortal_off_menu(self):
        if settings.immortal_mode:
            self.menu_items['immortal_off'].is_visible = True
        else:
            self.menu_items['immortal_off'].is_visible = False

    def handle_events(self, events: List[pg.event.Event], frame_time) -> None | State:
        self.star_timer += 1

        if self.star_timer >= 20:
            self.stars.append(Star())
            self.star_timer = 0

        for star in self.stars.copy():
            star.move()
            if star.is_off_screen():
                self.stars.remove(star)

        if self.game_start_animation:
            if self.gsa_frame_count >= self.gsa_frames:
                # game start animation is over → now go to game and reset animation values
                self.game_start_animation = False
                self.gsa_ship_y = self.gsa_ship_y_init
                # setting self.new_game to None to release the reference to the GameState object
                game = self.new_game
                self.new_game = None
                return game
            if self.gsa_frame_count < self.gsa_frames / 2:
                self.gsa_speed += self.gsa_acceleration
            else:
                self.gsa_speed -= self.gsa_acceleration
            self.gsa_ship_y -= self.gsa_speed
            # no further event handling anymore when we only animate the game start
            self.gsa_frame_count += 1
            return None

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
                    # In case of play and resume we only play the menu_sound_select sound in case music is off.
                    # Otherwise, it sounds odd when the sound is played and the music starts.
                    if not (self.active_item == 'play' or self.active_item == 'resume'):
                        pg.mixer.Sound.play(self.menu_sound_select)
                    elif not settings.play_music:
                        pg.mixer.Sound.play(self.menu_sound_select)
                if return_value:
                    return return_value

            if not settings.immortal_mode:
                # Add the event to the list
                self.last_keydown_events.append(event.unicode)
                # Keep only the last 4 events in the list
                if len(self.last_keydown_events) > 4:
                    self.last_keydown_events.pop(0)
                if ''.join(self.last_keydown_events) == 'immo':
                    return SetImmortalMode(self)

    def __handle_menu_selection(self) -> None | State:
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
            self.__handle_game_start_animation()
            # return NewFrameRateState to change frame rate, do not yet return GameState, first handle game start animation
            return NewFrameRateState(60)
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
        elif self.active_item == 'credits':
            return CreditsState(self)
        elif self.active_item == 'highscores':
            if settings.score_server_host:
                return HighscoreServerState(self)
            return HighscoreState(self)
        elif self.active_item == 'immortal_off':
            settings.immortal_mode = False
            self.set_running_game(None)
            self.set_immortal_off_menu()

    def __handle_game_start_animation(self):
        self.game_start_animation = True
        self.gsa_frame_count = 0
        self.new_game = GameState(self)
        ship = self.new_game.ship
        self.gsa_distance = screen.get_height() - ship.y + self.gsa_ship_y_init
        self.gsa_acceleration = self.gsa_distance / ((self.gsa_frames / 2) ** 2)  # Acceleration rate per frame
        if settings.play_sound:
            pg.mixer.Sound.play(self.gsa_sound_launch)

    def render(self):
        screen_ = screen
        if self.game_start_animation:
            screen_ = self.screen_alpha
            # clear alpha screen with transparent black
            screen_.fill((0, 0, 0, 0))
            alpha = int(255 * (1 - (self.gsa_frame_count / self.gsa_frames)))
            self.screen_alpha.set_alpha(alpha)
            # make stars more transparent as well as soon as alpha of menu is below the stars alpha
            if self.screen_alpha_stars.get_alpha() > alpha:
                self.screen_alpha_stars.set_alpha(alpha)

        screen.blit(settings.background_img, (0, 0))

        if self.ping_score_server_rc is not None:
            self.draw_ping_message()

        # Draw transparent stars – clear screen with transparent black
        self.screen_alpha_stars.fill((0, 0, 0, 0))
        for star in self.stars:
            star.draw_ex(screen_=self.screen_alpha_stars)
        screen.blit(self.screen_alpha_stars, (0, 0))

        total_size_menu_title = self._title_word1.get_width() + self._ship_img_with_fire.get_width() + self._title_word2.get_width()
        word1_pos_x = screen.get_width() / 2 - total_size_menu_title / 2
        img_pos_x = word1_pos_x + self._title_word1.get_width()
        word2_pos_x = img_pos_x + self._ship_img_with_fire.get_width()
        screen_.blit(self._title_word1, (word1_pos_x, self._title_y))
        # always draw ship without alpha → therefore screen not screen_ here
        if self.game_start_animation:
            screen.blit(self._ship_img_with_fire, (img_pos_x, self.gsa_ship_y))
            if self.gsa_ship_y < 0:
                # start to draw from downside as well, but take the size from GameState
                # always draw without alpha → therefore screen not screen_ here
                screen.blit(self.new_game.ship.ship_by_color['green'], (self.new_game.ship.x, screen.get_height() + self.gsa_ship_y))
        else:
            screen.blit(self._ship_img_no_fire, (img_pos_x, self.gsa_ship_y))
        screen_.blit(self._title_word2, (word2_pos_x, self._title_y))
        self._instructions.draw(screen_)

        for mi in self.menu_items.values():
            mi.draw(screen_)

        if self.game_start_animation:
            screen.blit(self.screen_alpha, (0, 0))

    def draw_ping_message(self):
        if self.ping_score_server_rc == 0:
            self.message_display = Message(self.ping_score_server_message, position='left', color=WHITE, alpha=64)
        else:
            self.message_display = Message(self.ping_score_server_message, position='left', color=DARK_RED)
        if self.menu_msg_time == 0:
            # initialise to time so we can stop at 5 secs
            self.menu_msg_time = time.time()
        if time.time() - self.menu_msg_time <= 5.0:
            self.message_display.draw()
        else:
            self.ping_score_server_rc = None

    def get_frame_rate(self) -> int:
        return 30

    # Callback for the async ping call at menu initialisation
    def on_score_server_ping(self, result):
        self.ping_score_server_rc = result['rc']
        self.ping_score_server_message = result['message']
