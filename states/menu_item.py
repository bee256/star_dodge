import pygame as pg
from enum import Enum
from os import path
from utils.paths import dir_images, dir_fonts
from utils.colors import LIGHT_BLUE, GRAY, WHITE


class MenuItemType(Enum):
    SELECT = 1
    TOGGLE = 2
    ENTRY = 3


class MenuItem:
    _class_is_initialised = False
    _menu_font: pg.font.Font
    _entry_font: pg.font.Font
    _screen: pg.Surface
    _toggle_on: pg.Surface
    _toggle_off: pg.Surface

    @staticmethod
    def initialise(screen: pg.Surface, menu_font_size):
        if MenuItem._class_is_initialised:
            return

        MenuItem._screen = screen
        MenuItem._menu_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Bold.ttf'), menu_font_size)
        MenuItem._entry_font = pg.font.Font(path.join(dir_fonts, 'SpaceGrotesk-Regular.ttf'), menu_font_size)
        MenuItem._toggle_on = pg.image.load(path.join(dir_images, 'toggle_on.png'))
        toggle_height = menu_font_size * 0.8
        toggle_width = toggle_height * MenuItem._toggle_on.get_width() / MenuItem._toggle_on.get_height()
        MenuItem._toggle_on = pg.transform.smoothscale(MenuItem._toggle_on, (toggle_width, toggle_height))
        MenuItem._toggle_off = pg.image.load(path.join(dir_images, 'toggle_off.png'))
        MenuItem._toggle_off = pg.transform.smoothscale(MenuItem._toggle_off, (toggle_width, toggle_height))

        MenuItem._class_is_initialised = True

    @staticmethod
    def get_rendered_size_of_menu_text(text: str) -> (int, int):
        if not MenuItem._class_is_initialised:
            raise ValueError(f"Class is not initialized. Call {__class__.__name__}.initialise() first.")

        label = MenuItem._menu_font.render(text, True, GRAY)
        return label.get_width(), label.get_height()

    def __init__(self, name: str, display_text: str, mitype: MenuItemType, position: (int, int), is_visible: bool):
        self.name = name
        self.display_text = display_text
        self.mitype = mitype
        self.pos_x = position[0]
        self.pos_y = position[1]
        self.is_visible = is_visible
        self.is_active = False

        self.toggle_value = True
        self.entry_value = None

    def draw(self):
        font = MenuItem._menu_font
        if not self.is_visible:
            return

        if self.is_active:
            label = font.render(self.display_text, True, LIGHT_BLUE)
        else:
            label = font.render(self.display_text, True, GRAY)

        MenuItem._screen.blit(label, (self.pos_x, self.pos_y))
        # the following two lines were just to show the boundaries of the menu item with a red rectangle
        # rect_position = (self.pos_x, self.pos_y, label.get_width(), label.get_height())
        # pg.draw.rect(MenuItem._screen, RED, rect_position, 1)

        if self.mitype == MenuItemType.TOGGLE:
            pos_x = self.pos_x + label.get_width() + label.get_height() / 2
            pox_y = self.pos_y + label.get_height() / 2 - MenuItem._toggle_on.get_height() / 2
            if self.toggle_value is True:
                MenuItem._screen.blit(MenuItem._toggle_on, (pos_x, pox_y))
            else:
                MenuItem._screen.blit(MenuItem._toggle_off, (pos_x, pox_y))
        elif self.mitype == MenuItemType.ENTRY:
            pos_x = self.pos_x + label.get_width()
            MenuItem._screen.blit(MenuItem._entry_font.render(self.entry_value, True, WHITE), (pos_x, self.pos_y))
