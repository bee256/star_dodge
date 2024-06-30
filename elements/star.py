import pygame as pg
import random

from utils.colors import *
from utils.settings import Settings

is_initialised = False
star_w: int
star_h: int
star_mask: pg.mask.Mask
star_vel_max: int
star_vel_min: int
STAR_COLOR_PALETTE = (WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, LIGHT_BLUE, LIGHT_GRAY, ORANGE, PURPLE, PINK)
screen: pg.Surface


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
    def initialise(screen_: pg.Surface):
        global screen, star_w, star_h, star_mask, star_vel_max, star_vel_min
        screen = screen_
        star_w = round(screen.get_width() / 150)
        star_h = round(screen.get_height() / 70)
        star_vel_max = round(screen.get_height() / 144)
        star_vel_min = round(screen.get_height() / 288)
        star_mask = pg.mask.Mask((star_w, star_h))
        star_mask.fill()
        settings = Settings()
        if settings.verbose:
            print(f"Star size is w: {star_w}, h: {star_h}, velocity min/max: {star_vel_min}/{star_vel_max}")
        Star._class_is_initialised = True

    def __init__(self):
        if not Star._class_is_initialised:
            raise ValueError(f"Class is not initialized. Call {__class__.__name__}.initialise() first.")

        star_x = random.randint(0, screen.get_width() - star_w)
        self.star_rect = pg.Rect(star_x, -star_h, star_w, star_h)
        self.color = STAR_COLOR_PALETTE[random.randint(0, len(STAR_COLOR_PALETTE) - 1)]
        self.velocity = random.randint(star_vel_min, star_vel_max)

    def draw(self):
        pg.draw.rect(screen, self.color, self.star_rect)

    def move(self):
        self.star_rect.y += self.velocity

    def is_off_screen(self):
        if self.star_rect.y > screen.get_height():
            return True
        return False

    def is_near_ship(self, ship):
        if self.star_rect.y + self.star_rect.height >= ship.y:
            return True
        return False

    def collides_with_ship(self, ship):
        if ship.mask.overlap(star_mask, (self.star_rect.x - ship.x, self.star_rect.y - ship.y)):
            return True
        return False
