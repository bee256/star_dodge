import pygame as pg
from os import path
from utils.paths import dir_fonts
from utils.settings import Settings
from utils.colors import GRAY

settings: Settings


class Message():
    def __init__(self, *args, position='right', color=GRAY, alpha: int = 255):
        global settings
        settings = Settings()
        instructions_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), round(settings.font_size_base * 0.6))
        self.instructions = []

        for item in args:
            # initialise the y position to 0 → will be updated afterwards
            rendered_text = instructions_font.render(item, 1, color)
            rendered_text_alpha = pg.Surface((rendered_text.get_width(), rendered_text.get_height()), pg.SRCALPHA)
            rendered_text_alpha.blit(rendered_text, (0, 0))
            rendered_text_alpha.set_alpha(alpha)  # Set the transparency level (0 is fully transparent, 255 is fully opaque)
            rendered_text = rendered_text_alpha

            self.instructions.append({'pos_y': 0, 'surface': rendered_text})

        line_height = self.instructions[0]['surface'].get_height()
        max_line_length = max(item['surface'].get_width() for item in self.instructions)
        if position == 'right':
            self.pos_x = settings.screen.get_width() - max_line_length - line_height
        else:
            self.pos_x = line_height
        num_total_items = len(args)

        for num, item in enumerate(self.instructions):
            # setting the y position for each item on the screen
            item['pos_y'] = settings.screen.get_height() - (num_total_items + 1 - num) * line_height

    def set_alpha(self, alpha: int):
        if alpha < 0 or alpha > 255:
            return

        for item in self.instructions:
            item['surface'].set_alpha(alpha)

    def draw(self, screen_: pg.Surface=None):
        screen = settings.screen
        if screen_ is not None:
            screen = screen_
        for item in self.instructions:
            screen.blit(item['surface'], (self.pos_x, item['pos_y']))
