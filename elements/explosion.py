import pygame as pg
from os import path
from utils.paths import dir_images
from utils.settings import Settings

SPRITE_WIDTH = 128
SPRITE_HEIGHT = 128
NUM_SPRITES = 39  # As the image is 1024 pixels wide and each sprite is 128 pixels
sprite_sheet = pg.image.load(path.join(dir_images, 'explosion_sprites.png'))


def get_sprite(x, y, explosion_size):
    # Create a new surface to store the sprite
    sprite = pg.Surface((SPRITE_WIDTH, SPRITE_HEIGHT), pg.SRCALPHA)
    # Blit (copy) a portion of the sprite sheet to the new surface
    sprite.blit(sprite_sheet, (0, 0), (x, y, SPRITE_HEIGHT, SPRITE_HEIGHT))
    sprite = pg.transform.smoothscale(sprite, (explosion_size, explosion_size))
    return sprite


# create Explosion class
class Explosion(pg.sprite.Sprite):
    _class_is_initialised = False
    _images = []

    @staticmethod
    def initialise(screen: pg.Surface):
        if Explosion._class_is_initialised:
            return

        settings = Settings()
        explosion_size = round(screen.get_width() / 12)
        if settings.verbose:
            print(f"Explosion size is: {explosion_size}")

        for i in range(NUM_SPRITES):
            sprite_x = i % 8 * SPRITE_WIDTH
            sprite_y = i // 8 * SPRITE_HEIGHT
            sprite = get_sprite(sprite_x, sprite_y, explosion_size)
            Explosion._images.append(sprite)

        Explosion._class_is_initialised = True

    def __init__(self, x, y):
        if not Explosion._class_is_initialised:
            raise ValueError(f"Class is not initialized. Call {__class__.__name__}.initialise() first.")

        super().__init__()
        self.images = Explosion._images
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.frame_counter = 0

    def update(self):
        explosion_speed = 1
        # update explosion animation
        self.frame_counter += 1

        if self.frame_counter >= explosion_speed:
            if self.index < len(self.images) - 1:
                self.frame_counter = 0
                self.index += 1
                self.image = self.images[self.index]
                return
            # here self.index is >= len(self.images) → animation is over
            self.kill()


# The main program is just for test purposes.
def main():
    pg.init()

    clock = pg.time.Clock()
    fps = 60

    screen_width = 1200
    screen_height = 800

    screen = pg.display.set_mode((screen_width, screen_height))
    pg.display.set_caption('Explosion Demo')

    # define colours
    # bg = (50, 50, 50)
    bg = (255, 255, 255)

    def draw_bg():
        screen.fill(bg)

    explosion_group = pg.sprite.Group()

    run = True
    i = 0

    my_images = []
    for i in range(NUM_SPRITES):
        sprite_x = i % 8 * SPRITE_WIDTH
        sprite_y = i // 8 * SPRITE_HEIGHT
        sprite = get_sprite(sprite_x, sprite_y, SPRITE_WIDTH)
        my_images.append(sprite)

    Explosion.initialise(screen)

    while run:
        clock.tick(fps)

        # draw background
        draw_bg()

        # draw the explosion fully for test purposes
        screen.blit(my_images[i % 38], (100, 100))
        i += 1

        # try out the sprite
        explosion_group.draw(screen)
        explosion_group.update()

        # event handler
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                explosion = Explosion(pos[0], pos[1])
                explosion_group.add(explosion)

        pg.display.update()

    pg.quit()


if __name__ == '__main__':
    main()
