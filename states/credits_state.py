import json
import os
import random
import sys
import time

import pygame as pg
from os import path
from typing import List

from states.helper import Message
from states.state import State
from utils.colors import LIGHT_BLUE, ORANGE, WHITE, RED, LIGHT_RED
from utils.paths import dir_fonts, dir_images
from utils.settings import Settings


class Credit:
    header_font_default: pg.font.Font = None
    line_font_default: pg.font.Font = None

    def __init__(self, *args: str, header: str, header2: str = None, color_header: pg.color = LIGHT_BLUE, color_line: pg.color = WHITE,
                 add_distance: float = 0,
                 header_font=None, line_font=None):
        settings = Settings()
        if Credit.header_font_default is None:
            Credit.header_font_default = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), settings.font_size_base)
        if Credit.line_font_default is None:
            Credit.line_font_default = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), round(settings.font_size_base * 0.8))

        if header_font is None:
            header_font = Credit.header_font_default
        if line_font is None:
            line_font = Credit.line_font_default
        self.header_font = header_font
        self.line_font = line_font
        self.header = self.header_font.render(header, True, color_header)
        self.header2 = None
        if header2 is not None:
            self.header2 = self.header_font.render(header2, True, color_header)
        self.max_width = self.header.get_width()
        self.add_distance = add_distance
        self.lines = []
        for line in list(args):
            line_rendered = self.line_font.render(line, True, color_line)
            self.lines.append(line_rendered)
            if line_rendered.get_width() > self.max_width:
                self.max_width = line_rendered.get_width()

    def draw(self, screen, x_pos, y_pos) -> int:
        x_pos = (screen.get_width() - self.header.get_width()) / 2
        screen.blit(self.header, (x_pos, y_pos))
        y_pos += self.header.get_height()
        if self.header2 is not None:
            x_pos = (screen.get_width() - self.header2.get_width()) / 2
            screen.blit(self.header2, (x_pos, y_pos))
            y_pos += self.header2.get_height()

        for line in self.lines:
            x_pos = (screen.get_width() - line.get_width()) / 2
            screen.blit(line, (x_pos, y_pos))
            y_pos += line.get_height()

        if self.add_distance:
            y_pos += self.add_distance
        return y_pos


class CreditsState(State):
    def __init__(self, menu_state: State):
        super().__init__()
        self.menu_state = menu_state

        self.settings = Settings()
        self.screen = self.settings.screen

        # Schriften
        self.title_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), round(self.settings.font_size_base * 2.5))
        self.credits_bigger_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'),
                                                round(self.settings.font_size_base * 1.25))

        # Texte
        self._title = self.title_font.render("CREDITS", True, LIGHT_BLUE)

        main_program_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        # Define the path to the JSON file relative to the script directory
        sw_ag_json = os.path.join(main_program_dir, 'data_no_git', 'sw_ag.json')

        sw_ag_names = None
        try:
            # Read the JSON file
            with open(sw_ag_json, 'r') as file:
                sw_ag_names = json.load(file)
        except Exception:
            pass

        if sw_ag_names is not None:
            random.shuffle(sw_ag_names)

        self._credits = []
        star_dodge_credit_strings = ['© 2024  Bernd Engist']
        if self.settings.app_version is not None:
            star_dodge_credit_strings.append(f"Version {self.settings.app_version}")
        if self.settings.git_commit is not None and self.settings.git_branch is not None:
            star_dodge_credit_strings.append(
                f"Built from git commit {self.settings.git_branch} {self.settings.git_commit}")
        if self.settings.git_commit_date is not None:
            star_dodge_credit_strings.append(
                f"Git commit date: {self.settings.git_commit_date}")
        self._credits.append(Credit(*star_dodge_credit_strings, header='Star Dodge'))
        self._credits.append(Credit('Spaceship designed by Freepik (www.freepik.com)', header='Graphics'))
        self._credits.append(
            Credit('Provided by Pixabay and YouTube Audio Library', 'Rocket launch by Philip Daniels', 'Rubble Crash by Alex Voxel',
                   header='Sounds'))
        self._credits.append(Credit('Planetary Paths by Joel Cummins and Andy Farag', header='Music'))
        self._credits.append(Credit('Space Grotesk by Florian Karsten', header='Font'))
        self._credits.append(
            Credit('The Open Source Community for providing incredible resources',
                   'Tech With Tim YouTube channel',
                   'The members of the FG-Software AG for all ideas and contributions',
                   'Bart and Michael for help and feedback on Python coding',
                   header='Thanks to'))
        self._credits.append(
            Credit('This game is licensed under the MIT License', 'For more information, visit github.com/bee256',
                   header='License', add_distance=self.screen.get_height() / 3))
        if sw_ag_names is not None:
            self._credits.append(
                Credit(*sw_ag_names,
                       header='FG-Software AG', header2='April-July 2024 in random order :-)', color_header=ORANGE,
                       header_font=self.credits_bigger_font, line_font=self.credits_bigger_font,
                       add_distance=self.screen.get_height() / 5))
            self._credits.append(
                Credit('All the players at the FG-Hock',
                       header='Special thanks to', add_distance=self.screen.get_height() / 3, header_font=self.credits_bigger_font,
                       line_font=self.credits_bigger_font,
                       color_line=LIGHT_RED))
        max_text_with = max(credit.max_width for credit in self._credits)
        self.x_pos = (self.screen.get_width() - max_text_with) / 2
        if self.x_pos < 0:
            self.x_pos = self.screen.get_width() * 0.1
        self.title_y_pos = self.screen.get_height() / 10
        self.y_pos = self.title_y_pos + self._title.get_height() * 1.5

        self.start_time = time.time()
        self._scroll_speed = 2
        self._credit_pos = self.screen.get_height()
        self._instructions = Message("Escape key to return to main menu")

    def handle_events(self, events: List[pg.event.Event], frame_time):
        for event in events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return self.menu_state

    def render(self):
        self.screen.blit(self.settings.background_img, (0, 0))
        self.screen.blit(self._title, (self.screen.get_width() / 2 - self._title.get_width() / 2, self.title_y_pos))
        self._instructions.draw()
        # self.scroll_credits()
        y_pos = self.y_pos
        for credit in self._credits:
            y_pos = credit.draw(self.screen, self.x_pos, y_pos)
            y_pos += credit.header.get_height() * 0.5
            if y_pos > self.screen.get_height():
                break  # we can stop drawing when we are off screen

        pg.display.flip()
        # begin to scroll after 2 secs
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= 2.0:
            self.title_y_pos -= self._scroll_speed
            self.y_pos -= self._scroll_speed

    def get_frame_rate(self) -> int:
        return 60
