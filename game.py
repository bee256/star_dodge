import pygame as pg
import time
import random
from os import path

# from pygame.locals import *

# os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
pg.font.init()
# Work in windowed mode
WIN = pg.display.set_mode((1200, 800))
# Set display mode to full-screen
# WIN = pg.display.set_mode((0, 0), pg.FULLSCREEN)    # pg.HWSURFACE | pg.DOUBLEBUF

info_display = pg.display.Info()
SCREEN_W, SCREEN_H = (info_display.current_w, info_display.current_h)
print(f"Screen w: {SCREEN_W}, h: {SCREEN_H}")

BG = pg.transform.scale(pg.image.load(path.join('assets', 'images', 'background.jpeg')), (SCREEN_W, SCREEN_H))

FONT_SIZE_BASE = int(SCREEN_W / 40)
SHIP_VEL = 5
STAR_W = int(SCREEN_W / 150)
STAR_H = int(SCREEN_H / 70)
STAR_VEL_MAX = 10
STAR_VEL_MIN = 5
STARS_CREATE_PER_INCREMENT = 4
print(f"Star w: {STAR_W}, h: {STAR_H}")
STAR_MASK = pg.mask.Mask((STAR_W, STAR_H))
STAR_MASK.fill()

TIME_FONT = pg.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), FONT_SIZE_BASE)
LOST_FONT = pg.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), FONT_SIZE_BASE * 2)
SOUND_CRASH = pg.mixer.Sound(path.join('assets', 'sound', 'rubble_crash.wav'))
SOUND_HIT = pg.mixer.Sound(path.join('assets', 'sound', 'metal_trash_can_filled_2.wav'))
pg.mixer.music.load(path.join('assets', 'sound', 'planetary_paths.mp3'), 'planet_paths')
HITS_MAX = 3

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Additional Colors
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIGHT_BLUE = (0, 160, 255)

# Gray Shades
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)

# Custom Colors
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 182, 193)

STAR_COLOR_PALETTE = (WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, LIGHT_BLUE, LIGHT_GRAY, ORANGE, PURPLE, PINK)


class Ship:
    def __init__(self):
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
        self.width = int(SCREEN_W / 28)
        self.height = self.width * image_aspect
        offset = self.height / 2

        # We scale each colored image after the color replacement and not before because of the antialiasing with smooth scale
        for col in color_set:
            self.ship_by_color[col] = pg.transform.smoothscale(self.ship_by_color[col], (self.width, self.height))

        self.mask = pg.mask.from_surface(self.ship_by_color['green'])
        self.x = int(SCREEN_W / 2 - self.width / 2)
        self.y = int(SCREEN_H - self.height - offset)

    def draw(self, color: str):
        WIN.blit(self.ship_by_color[color], (self.x, self.y))

    def draw_all_ships_for_test(self):
        i = 0
        for col in self.ship_by_color.keys():
            WIN.blit(self.ship_by_color[col], (i * self.width, 0))
            i = i + 1


class Star:
    def __init__(self):
        star_x = random.randint(0, SCREEN_W - STAR_W)
        self.star = pg.Rect(star_x, -STAR_H, STAR_W, STAR_H)
        self.color = STAR_COLOR_PALETTE[random.randint(0, len(STAR_COLOR_PALETTE) - 1)]
        self.velocity = random.randint(STAR_VEL_MIN, STAR_VEL_MAX)

    def draw(self):
        pg.draw.rect(WIN, self.color, self.star)

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


def draw_paused():
    paused_text = LOST_FONT.render("Paused!", 1, pg.Color(LIGHT_BLUE))
    WIN.blit(paused_text, (SCREEN_W / 2 - paused_text.get_width() / 2, SCREEN_H / 2 - paused_text.get_height() / 2))
    pg.display.flip()


def draw(ship, elapsed_time, stars, hits):
    WIN.blit(BG, (0, 0))
    # ship.draw_all_ships_for_test()

    color = 'green'
    if hits == 1:
        color = 'yellow'
    elif hits == 2:
        color = 'orange'
    elif hits >= 3:
        color = 'red'

    ship.draw(color)
    # WIN.blit(SHIP_G_MASK_IMAGE, (ship.x + PLAYER_W + 10, ship.y))

    for star in stars:
        star.draw()

    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    time_text = TIME_FONT.render(f"Time: {minutes:02d}:{seconds:02d}", 1, pg.Color(LIGHT_BLUE))
    WIN.blit(time_text, (30, 10))

    hits_text = TIME_FONT.render(f"Hits: {hits}", 1, color)
    WIN.blit(hits_text, (SCREEN_W - hits_text.get_width() - 30, 10))

    if hits >= 3:
        lost_text = LOST_FONT.render("Raumschiff am Arsch!", 1, pg.Color(212, 0, 0))
        WIN.blit(lost_text, (SCREEN_W / 2 - lost_text.get_width() / 2, SCREEN_H / 2 - lost_text.get_height() / 2))

    pg.display.flip()


def main():
    # Run the game loop
    run = True
    ship = Ship()
    print(f"Ship dimensions are w: {ship.width}, h: {ship.height}")

    clock = pg.time.Clock()
    # print(f"Framerate: {clock.get_fps():.2f}")
    start_time = time.time()

    star_add_increment = 1500
    star_create_timer = 0

    stars = []
    is_hit = False
    hits = 0
    is_paused = False
    pause_start = 0

    pg.mixer.music.play(loops=-1)
    pg.mouse.set_visible(False)

    while run:
        star_create_timer += clock.tick(60)
        # clock_tick_num_calls += 1
        # if clock_tick_num_calls == 50:
        #     print(f"Framerate: {clock.get_fps():.2f}")
        #     clock_tick_num_calls = 0

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    is_paused = not is_paused
                    if is_paused:
                        pause_start = time.time()
                        draw_paused()
                    else:
                        start_time += time.time() - pause_start

        if is_paused:
            continue

        elapsed_time = time.time() - start_time

        # game logic: every star_add_increment we create a bunch of stars
        if star_create_timer > star_add_increment:
            for i in range(STARS_CREATE_PER_INCREMENT):
                star = Star()
                stars.append(star)

            # here we decrease star_add_increment, so that starts get created faster and faster, but not faster than a threshold
            star_add_increment = max(150, star_add_increment - 50)
            star_create_timer = 0

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and ship.x - SHIP_VEL >= 0:
            ship.x -= SHIP_VEL
        if keys[pg.K_RIGHT] and ship.x + SHIP_VEL + ship.width <= SCREEN_W:
            ship.x += SHIP_VEL
        if keys[pg.K_ESCAPE]:
            pg.mixer.music.fadeout(1000)
            pg.time.delay(1100)
            break  # break out of while look do not draw anymore

        for star in stars.copy():
            star.move()
            if star.is_off_screen():
                stars.remove(star)
            elif star.is_near_ship(ship):
                if star.collides_with_ship(ship):
                    stars.remove(star)
                    is_hit = True
                    break

        if is_hit:
            hits += 1
            if hits < 3:
                pg.mixer.Sound.play(SOUND_HIT)
                is_hit = False
            else:
                pg.mixer.Sound.play(SOUND_CRASH)
                pg.mixer.music.fadeout(2500)
                run = False

        # print(f"Num stars: {len(stars)}", end=' ')
        draw(ship, elapsed_time, stars, hits)
    # end of game loop

    if is_hit:
        # if we ended the loop with is hit it means that game is over
        pg.time.delay(3000)

    pg.quit()


if __name__ == '__main__':
    main()
