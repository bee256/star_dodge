import pygame as pg
from os import path


class Ship:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        ship = pg.image.load(path.join('assets', 'images', 'space_ship.png'))
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

        # calculate aspect ratio
        image_aspect = ship.get_height() / ship.get_width()
        # use a reasonable width in relation so screen
        self.width = round(screen.get_width() / 28)
        # height is then derived using the aspect ratio
        self.height = round(self.width * image_aspect)
        # the speed in which we move the ship is in relation to the size and thus relates to the screen as well
        self.__velocity = round(self.width / 12)
        offset = self.height / 2

        # We scale each colored image after the color replacement and not before because of the antialiasing with smooth scale
        for col in color_set:
            self.ship_by_color[col] = pg.transform.smoothscale(self.ship_by_color[col], (self.width, self.height))

        self.mask = pg.mask.from_surface(self.ship_by_color['green'])
        self.x = round(screen.get_width() / 2 - self.width / 2)
        self.y = round(screen.get_height() - self.height - offset)
        print(f"Ship width: {self.width}, height: {self.height}, velocity: {self.__velocity}")

    def draw(self, color: str):
        self.screen.blit(self.ship_by_color[color], (self.x, self.y))

    def move_left(self):
        if self.x - self.__velocity >= 0:
            self.x -= self.__velocity

    def move_right(self):
        if self.x + self.__velocity + self.width <= self.screen.get_width():
            self.x += self.__velocity

    def draw_all_ships_for_test(self):
        i = 0
        for col in self.ship_by_color.keys():
            self.screen.blit(self.ship_by_color[col], (i * self.width, 0))
            i = i + 1
