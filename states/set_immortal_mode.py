import pygame as pg
from os import path
import time
from typing import List

from states.state import State
from utils.colors import LIGHT_BLUE, WHITE, GRAY, DARK_RED, DARK_GREEN
from utils.paths import dir_fonts
from utils.settings import Settings

settings: Settings
screen: pg.Surface

CHEAT_CODE = 'immo'


class SetImmortalMode(State):
    def __init__(self, menu_state: State):
        self.menu_state = menu_state

        global screen, settings
        settings = Settings()
        screen = settings.screen

        self._entry_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), round(settings.font_size_base * 1.5))
        self._title_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), settings.font_size_base * 2)
        self.show_hint = None
        self._title = self._title_font.render("ENTER THE IMMORTAL CODE", 1, LIGHT_BLUE)
        hint_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), round(settings.font_size_base * 0.75))
        self._empty_hint = hint_font.render("You got no code? So go play like a noob …", 1, DARK_RED)
        self._wrong_input = hint_font.render("Hahaha! You don’t know the immortal code …", 1, DARK_RED)
        self._cheat_correct = hint_font.render("Yeah! You are now immortal …", 1, DARK_GREEN)
        self._immortal_turn_off = hint_font.render("Press any key to turn immortal mode off or Escape to keep it on", 1, DARK_GREEN)
        if settings.immortal_mode:
            self._title = self._title_font.render("YOU ARE IMMORTAL", 1, DARK_GREEN)
            self.show_hint = self._immortal_turn_off

        ibox_w = round(screen.get_width() / 2.2)
        ibox_h = self._entry_font.get_height() + 20
        ibox_x = round((screen.get_width() - ibox_w) / 2)
        ibox_y = round(screen.get_height() / 2)
        self.input_box = pg.Rect(ibox_x, ibox_y, ibox_w, ibox_h)
        self.real_text = ''
        self.star_text = ''
        self.cursor_visible = True  # Cursor visibility
        self.cursor_blink_time = time.time() + 0.5  # Time when cursor should toggle visibility

    def handle_events(self, events: List[pg.event.Event], frame_time):
        for event in events:
            if not event.type == pg.KEYDOWN:
                continue
            if event.key == pg.K_ESCAPE:
                return self.menu_state
            if settings.immortal_mode:
                # Handle any key to turn immortal mode off
                settings.immortal_mode = False
                # Cancel running game so no one can cheat a score using immortal mode
                self.menu_state.set_running_game(None)
                self.menu_state.set_immortal_off_menu()
                if settings.verbose:
                    print("Immortal mode turned off!")
                return self.menu_state
            if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                if self.real_text.strip() == "":
                    self.show_hint = self._empty_hint
                    self.real_text = ""
                    self.star_text = ""
                    return
                if self.real_text == CHEAT_CODE:
                    settings.immortal_mode = True
                    self.menu_state.set_immortal_off_menu()
                    if settings.verbose:
                        print("Yeah! You are now immortal!")
                    self.show_hint = self._cheat_correct
                    self.render()
                    pg.display.flip()
                    pg.time.delay(1200)
                    return self.menu_state
                else:
                    self.show_hint = self._wrong_input
            elif event.key == pg.K_BACKSPACE:
                self.real_text = self.real_text[:-1]
                self.star_text = self.star_text[:-1]
            else:
                self.show_hint = None
                self.real_text += event.unicode
                self.star_text += "*"

    def render(self):
        screen.blit(settings.background_img, (0, 0))
        screen.blit(self._title, (screen.get_width() / 2 - self._title.get_width() / 2, screen.get_height() / 5))

        if settings.immortal_mode:
            x = self.input_box.x + (self.input_box.width - self.show_hint.get_width()) / 2
            screen.blit(self.show_hint, (x, self.input_box.y + self.input_box.height + self.show_hint.get_height() / 2))
            return

        if time.time() > self.cursor_blink_time:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_time = time.time() + 0.5

        # Render text
        txt_surface = self._entry_font.render(self.star_text, True, WHITE)
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
        if self.show_hint:
            x = self.input_box.x + (self.input_box.width - self.show_hint.get_width()) / 2
            screen.blit(self.show_hint, (x, self.input_box.y + self.input_box.height + self.show_hint.get_height() / 2))

    def get_frame_rate(self) -> int:
        return 20
