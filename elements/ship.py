import pygame as pg
from os import path

from utils.paths import dir_images


class Ship:
    """
    This class creates a ship from a graphic file, scales according to the size of the surface it shall be drawn on,
    animates the ship and draws it.

    Attributes:
        screen (pygame.Surface): Surface where the ship is drawn on
        width (float): width of the ship
        height (float): height of the ship
        mask (pygame.mask): The mask of the ship (taken from the image) for collision detection
        x (int): x coordinate of the ship's surrounding rectangle
        y (int): y coordinate of the ship's surrounding rectangle

    Methods:
        draw(): draw on screen
        move_left(): move the ship to the left (will not move off-screen)
        move_right(): move the ship to the right (will not move off-screen)
    """
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        # create a dictionary which stores the ship images by color
        self.ship_by_color = {}
        # the graphics loaded has a ship in grey color with RGB(100,100,100) → create colorful ships by replacing gray
        # orig_color = pg.color.Color(100, 100, 100)
        color_set = ('green', 'yellow', 'orange', 'red')
        for index, col in enumerate(color_set):
            self.ship_by_color[col] = pg.image.load(path.join(dir_images, f"space_ship3_{index}{col}.png"))

        # calculate aspect ratio
        image_aspect = self.ship_by_color['green'].get_height() / self.ship_by_color['green'].get_width()
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
