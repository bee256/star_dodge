import pygame as pg
from os import path
import time
from typing import List

from states.state import State
from utils.colors import LIGHT_BLUE, WHITE, GRAY
from utils.paths import dir_fonts
from utils.settings import Settings

settings: Settings
screen: pg.Surface


class SetPlayerState(State):
    def __init__(self, menu_state: State):
        self.menu_state = menu_state

        global screen, settings
        settings = Settings()
        screen = settings.screen

        self._entry_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), round(settings.font_size_base * 1.5))
        self._title_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), settings.font_size_base * 2)
        self._title = self._title_font.render("ENTER PLAYER", 1, LIGHT_BLUE)

        ibox_w = round(screen.get_width() / 2.2)
        ibox_h = self._entry_font.get_height() + 20
        ibox_x = round((screen.get_width() - ibox_w) / 2)
        ibox_y = round(screen.get_height() / 2)
        self.input_box = pg.Rect(ibox_x, ibox_y, ibox_w, ibox_h)
        self.user_text = ''
        self.cursor_visible = True  # Cursor visibility
        self.cursor_blink_time = time.time() + 0.5  # Time when cursor should toggle visibility

    def handle_events(self, events: List[pg.event.Event], frame_time):
        for event in events:
            if not event.type == pg.KEYDOWN:
                continue
            if event.key == pg.K_ESCAPE:
                return self.menu_state
            if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                settings.player_name = self.user_text
                self.menu_state.set_player()
                return self.menu_state
            elif event.key == pg.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            else:
                self.user_text += event.unicode

    def render(self):
        screen.blit(settings.background_img, (0, 0))
        screen.blit(self._title, (screen.get_width() / 2 - self._title.get_width() / 2, screen.get_height() / 5))

        if time.time() > self.cursor_blink_time:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = time.time() + 0.5

        # Render text
        txt_surface = self._entry_font.render(self.user_text, True, WHITE)
        # width = max(300, txt_surface.get_width()+10)
        # self.input_box.w = width
        screen.blit(txt_surface, (self.input_box.x + 10, self.input_box.y + 5))

        # Render cursor
        if self.cursor_visible:
            cursor_x = self.input_box.x + txt_surface.get_width() + 15
            cursor_y = self.input_box.y + 10
            cursor = pg.Rect(cursor_x, cursor_y, 2, txt_surface.get_height())
            pg.draw.rect(screen, WHITE, cursor)

        # Render the input box
        pg.draw.rect(screen, GRAY, self.input_box, 2)

    def get_frame_rate(self) -> int:
        return 20
