import pygame as pg
from os import path
from typing import List

from states.state import State
from utils.colors import LIGHT_BLUE, ORANGE, WHITE, RED
from utils.paths import dir_fonts
from utils.settings import Settings


class CreditsState(State):
    def __init__(self, menu_state: State):
        super().__init__()
        self.menu_state = menu_state

        self.settings = Settings()
        self.screen = self.settings.screen

        # Schriften
        self._title_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), self.settings.font_size_base * 4)
        self._header_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), self.settings.font_size_base * 2)
        self._name_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), int(self.settings.font_size_base * 2))
        self._all_players_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), int(self.settings.font_size_base * 5))

        # Texte
        self._title = self._title_font.render("CREDITS", True, LIGHT_BLUE)

        self._credits = [
            ("AG-Leiter:", "Bernd"),
            ("AG-Teilnehmer:", "1"),
            ("","2"),
            ("","3"),
            ("","4"),
            ("","5"),
            ("","6"),
            ("","7"),

            ("Special Thanks to:", "All Players!")
        ]
        self._scroll_speed = 1
        self._credit_pos = self.screen.get_height()

    def handle_events(self, events: List[pg.event.Event], frame_time):
        for event in events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return self.menu_state

    def render(self):
        self.screen.blit(self.settings.background_img, (0, 0))
        title_y_pos = self.screen.get_height() / 50
        self.screen.blit(self._title, (self.screen.get_width() / 2 - self._title.get_width() / 2, title_y_pos))
        self.scroll_credits()
        pg.display.flip()

    def scroll_credits(self):
        self._credit_pos -= self._scroll_speed * 2
        screen_width = self.screen.get_width()

        y_offset = self._credit_pos
        title_y_pos = self.screen.get_height() / 10
        title_height = self._title.get_height()
        fade_out_start = title_y_pos - 50
        fade_out_end = title_y_pos + title_height + 50

        for header, name in self._credits:
            header_text = self._header_font.render(header, True, ORANGE)
            name_text = self._name_font.render(name, True, WHITE)
            all_players_text = self._all_players_font.render(name, True, RED)

            header_x = screen_width / 2 - header_text.get_width() / 2
            name_x = screen_width / 2 - name_text.get_width() / 2
            all_players_x = screen_width / 2 - all_players_text.get_width() / 2

            # Calculate alpha based on position relative to fade-out region
            if fade_out_start <= y_offset <= fade_out_end:
                alpha = int(255 * (y_offset - fade_out_start) / (fade_out_end - fade_out_start))
            elif y_offset < title_y_pos:
                alpha = 0
            else:
                alpha = 255

            header_text.set_alpha(alpha)
            name_text.set_alpha(alpha)
            all_players_text.set_alpha(alpha)

            if header != "":
                if header != "AG-Leiter:":
                    y_offset += name_text.get_height() - 60
                self.screen.blit(header_text, (header_x, y_offset))
                y_offset += header_text.get_height() + 5
                if name == "All Players!":
                    self.screen.blit(all_players_text, (all_players_x, y_offset))
                else:
                    self.screen.blit(name_text, (name_x, y_offset))
                    y_offset += name_text.get_height() + 20
            else:
                self.screen.blit(name_text, (name_x, y_offset))
                y_offset += name_text.get_height() + 20

        # Credits fortlaufend scrollen lassen
        if y_offset < 0:
            self._credit_pos = self.screen.get_height()

    def get_frame_rate(self) -> int:
        return 40
