import pygame as pg
import random

from game import SCREEN_W, SCREEN_H
from colors import *

STAR_W = int(SCREEN_W / 150)
STAR_H = int(SCREEN_H / 70)
STAR_VEL_MAX = 10
STAR_VEL_MIN = 5
print(f"Star w: {STAR_W}, h: {STAR_H}")
STAR_MASK = pg.mask.Mask((STAR_W, STAR_H))
STAR_MASK.fill()
STAR_COLOR_PALETTE = (WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, LIGHT_BLUE, LIGHT_GRAY, ORANGE, PURPLE, PINK)


class Star:
    def __init__(self, screen):
        self.screen = screen
        star_x = random.randint(0, SCREEN_W - STAR_W)
        self.star = pg.Rect(star_x, -STAR_H, STAR_W, STAR_H)
        self.color = STAR_COLOR_PALETTE[random.randint(0, len(STAR_COLOR_PALETTE) - 1)]
        self.velocity = random.randint(STAR_VEL_MIN, STAR_VEL_MAX)

    def draw(self):
        pg.draw.rect(self.screen, self.color, self.star)

    def move(self):
        self.star.y += self.velocity

    def is_off_screen(self):
        if self.star.y > SCREEN_H:
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
