import pygame as pg
import random

from colors import *

is_initialised = False
STAR_W: int
STAR_H: int
STAR_MASK: pg.mask.Mask
STAR_VEL_MAX: int
STAR_VEL_MIN: int
STAR_COLOR_PALETTE = (WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, LIGHT_BLUE, LIGHT_GRAY, ORANGE, PURPLE, PINK)
SCREEN: pg.Surface


class Star:
    """
    This class implements stars as rectangles with a random color from a color palette and moves them with a
    random velocity.

    Attributes:
        star_rect (pygame.Rect): the rectangle which is drawn on screen
        color: a randomly chosen color from a color palette
        velocity: a random chosen velocity from a certain range

    Methods:
        draw(): draw on screen
        move(): move the star vertically down the screen according to the velocity
        is_off_screen(): determines if the star has been moved outside the visible area of the screen
        is_near_ship(): determines if the star is close to the y coordinates of the ship
        collides_with_ship(): determines if the star collides with the ship
    """
    _class_is_initialised = False

    @staticmethod
    def initialise(screen: pg.Surface):
        global SCREEN, STAR_W, STAR_H, STAR_MASK, STAR_VEL_MAX, STAR_VEL_MIN
        SCREEN = screen
        STAR_W = round(screen.get_width() / 150)
        STAR_H = round(screen.get_height() / 70)
        STAR_VEL_MAX = round(screen.get_height() / 144)
        STAR_VEL_MIN = round(screen.get_height() / 288)
        STAR_MASK = pg.mask.Mask((STAR_W, STAR_H))
        STAR_MASK.fill()
        print(f"Star size is w: {STAR_W}, h: {STAR_H}, velocity min/max: {STAR_VEL_MIN}/{STAR_VEL_MAX}")
        Star._class_is_initialised = True

    def __init__(self):
        if not Star._class_is_initialised:
            raise ValueError("Class is not initialized. Call Star.initialise() first.")

        star_x = random.randint(0, SCREEN.get_width() - STAR_W)
        self.star_rect = pg.Rect(star_x, -STAR_H, STAR_W, STAR_H)
        self.color = STAR_COLOR_PALETTE[random.randint(0, len(STAR_COLOR_PALETTE) - 1)]
        self.velocity = random.randint(STAR_VEL_MIN, STAR_VEL_MAX)

    def draw(self):
        pg.draw.rect(SCREEN, self.color, self.star_rect)

    def move(self):
        self.star_rect.y += self.velocity

    def is_off_screen(self):
        if self.star_rect.y > SCREEN.get_height():
            return True
        return False

    def is_near_ship(self, ship):
        if self.star_rect.y + self.star_rect.height >= ship.y:
            return True
        return False

    def collides_with_ship(self, ship):
        if ship.mask.overlap(STAR_MASK, (self.star_rect.x - ship.x, self.star_rect.y - ship.y)):
            return True
        return False
