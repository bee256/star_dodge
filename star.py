import pygame as pg
import random

from colors import *

is_initialised = False
STAR_W: int
STAR_H: int
STAR_MASK: pg.mask.Mask
STAR_VEL_MAX = 10
STAR_VEL_MIN = 5
STAR_COLOR_PALETTE = (WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, LIGHT_BLUE, LIGHT_GRAY, ORANGE, PURPLE, PINK)
SCREEN: pg.Surface


class Star:
    _class_is_initialised = False
    @staticmethod
    def initialise(screen: pg.Surface):
        global SCREEN, STAR_W, STAR_H, STAR_MASK
        SCREEN = screen
        STAR_W = int(screen.get_width() / 150)
        STAR_H = int(screen.get_height() / 70)
        STAR_MASK = pg.mask.Mask((STAR_W, STAR_H))
        STAR_MASK.fill()
        print(f"Star size is w: {STAR_W}, h: {STAR_H}")
        Star._class_is_initialised = True

    def __init__(self):
        if not Star._class_is_initialised:
            raise ValueError("Class is not initialized. Call Star.initialise() first.")

        star_x = random.randint(0, SCREEN.get_width() - STAR_W)
        self.star = pg.Rect(star_x, -STAR_H, STAR_W, STAR_H)
        self.color = STAR_COLOR_PALETTE[random.randint(0, len(STAR_COLOR_PALETTE) - 1)]
        self.velocity = random.randint(STAR_VEL_MIN, STAR_VEL_MAX)

    def draw(self):
        pg.draw.rect(SCREEN, self.color, self.star)

    def move(self):
        self.star.y += self.velocity

    def is_off_screen(self):
        if self.star.y > SCREEN.get_height():
            return True
        return False

    def is_near_ship(self, ship):
        if self.star.y + self.star.height >= ship.y:
            return True
        return False

    def collides_with_ship(self, ship):
        if ship.mask.overlap(STAR_MASK, (self.star.x - ship.x, self.star.y - ship.y)):
            return True
        return False
