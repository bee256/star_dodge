import pygame as pg
from os import path

SHIP_VEL = 5


class Ship:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        ship = pg.image.load(path.join('assets', 'images', 'space_ship.png')).convert_alpha()
        # create a dictionary which stores the ship images by color
        self.ship_by_color = {}
        # the graphics loaded has a ship in grey color with RGB(100,100,100) → create colorful ships by replacing gray
        old_color = pg.color.Color(100, 100, 100)
        color_set = ('green', 'yellow', 'orange', 'red')
        for col in color_set:
            self.ship_by_color[col] = ship.copy()
            new_color = pg.color.Color(col)
            pixel_array = pg.PixelArray(self.ship_by_color[col])
            pixel_array.replace(old_color, new_color)

        image_aspect = ship.get_height() / ship.get_width()
        self.width = int(screen.get_width() / 28)
        self.height = self.width * image_aspect
        offset = self.height / 2

        # We scale each colored image after the color replacement and not before because of the antialiasing with smooth scale
        for col in color_set:
            self.ship_by_color[col] = pg.transform.smoothscale(self.ship_by_color[col], (self.width, self.height))

        self.mask = pg.mask.from_surface(self.ship_by_color['green'])
        self.x = int(screen.get_width() / 2 - self.width / 2)
        self.y = int(screen.get_height() - self.height - offset)

    def draw(self, color: str):
        self.screen.blit(self.ship_by_color[color], (self.x, self.y))

    def move_left(self):
        if self.x - SHIP_VEL >= 0:
            self.x -= SHIP_VEL

    def move_right(self):
        if self.x + SHIP_VEL + self.width <= self.screen.get_width():
            self.x += SHIP_VEL

    def draw_all_ships_for_test(self):
        i = 0
        for col in self.ship_by_color.keys():
            self.screen.blit(self.ship_by_color[col], (i * self.width, 0))
            i = i + 1

