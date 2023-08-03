import pygame
import time
import random
from os import path
# from pygame.locals import *

# os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.font.init()
info_display = pygame.display.Info()
SCREEN_W, SCREEN_H = (info_display.current_w, info_display.current_h)
print(f"Screen w: {SCREEN_W}, h: {SCREEN_H}")

# Set display mode to full-screen
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
BG = pygame.transform.scale(pygame.image.load(path.join('assets', 'images', 'background.jpeg')), (SCREEN_W, SCREEN_H))

FONT_SIZE_BASE = int(SCREEN_W / 40)
PLAYER_VEL = 5
STAR_W = int(SCREEN_W / 150)
STAR_H = int(SCREEN_H / 70)
STAR_VEL = 8
print(f"Star w: {STAR_W}, h: {STAR_H}")
TIME_FONT = pygame.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), FONT_SIZE_BASE)
LOST_FONT = pygame.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), FONT_SIZE_BASE * 2)
SOUND_CRASH = pygame.mixer.Sound(path.join('assets', 'sound', 'rubble_crash.wav'))
SOUND_HIT = pygame.mixer.Sound(path.join('assets', 'sound', 'metal_trash_can_filled_2.wav'))
pygame.mixer.music.load(path.join('assets', 'sound', 'planetary_paths.mp3'), 'planet_paths')
HITS_MAX = 3


class Ship():
    def __init__(self):
        ship = pygame.image.load(path.join('assets', 'images', 'space_ship.png')).convert_alpha()
        # create a dictionary which stores the ship images by color
        self.ship_by_color = {}
        # the graphics loaded has a ship in grey color with RGB(100,100,100) → create colorful ships by replacing gray
        old_color = pygame.color.Color(100, 100, 100)
        color_set = ('green', 'yellow', 'orange', 'red')
        for col in color_set:
            self.ship_by_color[col] = ship.copy()
            new_color = pygame.color.Color(col)
            pixel_array = pygame.PixelArray(self.ship_by_color[col])
            pixel_array.replace(old_color, new_color)

        image_aspect = ship.get_height() / ship.get_width()
        self.width = int(SCREEN_W / 28)
        self.height = self.width * image_aspect
        offset = self.height / 2

        # We scale each colorised image after the color replacement and not before because of the anti-aliasing with smoothscale
        for col in color_set:
            self.ship_by_color[col] = pygame.transform.smoothscale(self.ship_by_color[col], (self.width, self.height))

        self.mask = pygame.mask.from_surface(self.ship_by_color['green'])
        self.x = int(SCREEN_W / 2 - self.width / 2)
        self.y = int(SCREEN_H - self.height - offset)

    def draw(self, color: str):
        WIN.blit(self.ship_by_color[color], (self.x, self.y))

    def draw_all_ships_for_test(self):
        i = 0
        for col in self.ship_by_color.keys():
            WIN.blit(self.ship_by_color[col], (i * self.width, 0))
            i = i + 1


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
        pygame.draw.rect(WIN, 'white', star)

    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    time_text = TIME_FONT.render(f"Time: {minutes:02d}:{seconds:02d}", 1, pygame.Color(0, 160, 255))
    WIN.blit(time_text, (30, 10))

    hits_text = TIME_FONT.render(f"Hits: {hits}", 1, color)
    WIN.blit(hits_text, (SCREEN_W - hits_text.get_width() - 30, 10))

    if hits >= 3:
        lost_text = LOST_FONT.render("Raumschiff am Arsch!", 1, pygame.Color(212, 0, 0))
        WIN.blit(lost_text, (SCREEN_W/2 - lost_text.get_width()/2, SCREEN_H/2 - lost_text.get_height()/2))

    pygame.display.update()


def main():
    # Run the game loop
    run = True
    # player = pygame.Rect(SCREEN_W / 2 - PLAYER_W / 2, SCREEN_H - PLAYER_H - PLAYER_OFFSET, PLAYER_W, PLAYER_H)
    ship = Ship()
    print(f"Ship w: {ship.width}, h: {ship.height}")

    clock = pygame.time.Clock()
    # print(f"Framerate: {clock.get_fps():.2f}")
    start_time = time.time()

    star_add_increment = 1500
    star_timer = 0

    stars = []
    star_mask = pygame.mask.Mask((STAR_W, STAR_H))
    star_mask.fill()

    is_hit = False
    hits = 0

    pygame.mixer.music.play(loops=-1)
    pygame.mouse.set_visible(False)

    # clock_tick_num_calls = 0

    while run:
        star_timer += clock.tick(60)
        # clock_tick_num_calls += 1
        # if clock_tick_num_calls == 50:
        #     print(f"Framerate: {clock.get_fps():.2f}")
        #     clock_tick_num_calls = 0

        elapsed_time = time.time() - start_time

        if star_timer > star_add_increment:
            for i in range(3):
                star_x = random.randint(0, SCREEN_W - STAR_W)
                star = pygame.Rect(star_x, -STAR_H, STAR_W, STAR_H)
                stars.append(star)

            star_add_increment = max(150, star_add_increment - 50)
            star_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and ship.x - PLAYER_VEL >= 0:
            ship.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and ship.x + PLAYER_VEL + ship.width <= SCREEN_W:
            ship.x += PLAYER_VEL
        if keys[pygame.K_ESCAPE]:
            pygame.mixer.music.fadeout(1000)
            pygame.time.delay(1100)
            break

        for star in stars[:]:
            star.y += STAR_VEL
            if star.y > SCREEN_H:
                stars.remove(star)
            elif star.y + star.height >= ship.y:
                if (ship.mask.overlap(star_mask, (star.x - ship.x, star.y - ship.y))):
                    stars.remove(star)
                    is_hit = True
                    break

        if is_hit:
            hits += 1
            if hits < 3:
                pygame.mixer.Sound.play(SOUND_HIT)
                is_hit = False
            else:
                pygame.mixer.Sound.play(SOUND_CRASH)
                pygame.mixer.music.fadeout(2500)
                run = False

        # print(f"Num stars: {len(stars)}", end=' ')

        draw(ship, elapsed_time, stars, hits)

    if is_hit:
        pygame.time.delay(3000)

    pygame.quit()


if __name__ == '__main__':
    main()
