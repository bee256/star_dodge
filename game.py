import pygame
import time
import random
pygame.font.init()
import os
# from pygame.locals import *

# os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
info_display = pygame.display.Info()
SCREEN_W, SCREEN_H = (info_display.current_w, info_display.current_h)
SCREEN_W, SCREEN_H = (info_display.current_w, info_display.current_h)
print(f"Screen w: {SCREEN_W}, h: {SCREEN_H}")

# Set display mode to full-screen
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

#BG = pygame.image.load("Python-Game-Dev-Intro-main/bg.jpeg")
BG = pygame.transform.scale(pygame.image.load('assets/images/background.jpeg'), (SCREEN_W, SCREEN_H))

PLAYER_W = int(SCREEN_W / 40)
PLAYER_H = int(SCREEN_H / 18)
PLAYER_OFFSET = PLAYER_H / 2
PLAYER_VEL = 5
print(f"Player w: {PLAYER_W}, h: {PLAYER_H}")
STAR_W = int(SCREEN_W / 150)
STAR_H = int(SCREEN_H / 70)
STAR_VEL = 8
print(f"Star w: {STAR_W}, h: {STAR_H}")
TIME_FONT = pygame.font.SysFont('comicsans', PLAYER_H)
LOST_FONT = pygame.font.SysFont('comicsans', PLAYER_H * 2)
SOUND_CRASH = pygame.mixer.Sound("assets/sound/rubble_crash.wav")
SOUND_HIT = pygame.mixer.Sound("assets/sound/metal_trash_can_filled_2.wav")
SOUND_MUSIC = pygame.mixer.music.load("assets/sound/planetary_paths.mp3", 'planet_paths')
HITS_MAX = 3

def draw(player, elapsed_time, stars, hits):
    WIN.blit(BG, (0, 0))

    color = 'green'
    if hits == 1:
        color = 'yellow'
    elif hits == 2:
        color = 'orange'
    elif hits >= 3:
        color = 'red'

    pygame.draw.rect(WIN, color, player)

    for star in stars:
        pygame.draw.rect(WIN, 'white', star)

    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    time_text = TIME_FONT.render(f"Time: {minutes:02d}:{seconds:02d}", 1, pygame.Color(0, 160, 255))
    WIN.blit(time_text, (20, 20))

    hits_text = TIME_FONT.render(f"Hits: {hits}", 1, color)
    WIN.blit(hits_text, (SCREEN_W - hits_text.get_width() - 20, 20))

    if hits >= 3:
        lost_text = LOST_FONT.render("Raumschiff am Arsch!", 1, pygame.Color(212, 0, 0))
        WIN.blit(lost_text, (SCREEN_W/2 - lost_text.get_width()/2, SCREEN_H/2 - lost_text.get_height()/2))

    pygame.display.update()


def main():
    # Run the game loop
    run = True
    player = pygame.Rect(SCREEN_W / 2 + PLAYER_W / 2, SCREEN_H - PLAYER_H - PLAYER_OFFSET, PLAYER_W, PLAYER_H)
    clock = pygame.time.Clock()
    # print(f"Framerate: {clock.get_fps():.2f}")
    start_time = time.time()
    elapsed_time = 0

    star_add_increment = 1500
    star_timer = 0

    stars = []
    is_hit = False
    hits = 0

    pygame.mixer.music.play()
    pygame.mouse.set_visible(False)

    clock_tick_num_calls = 0

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
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= SCREEN_W:
            player.x += PLAYER_VEL
        if keys[pygame.K_ESCAPE]:
            pygame.mixer.music.fadeout(1000)
            pygame.time.delay(1100)
            break

        for star in stars[:]:
            star.y += STAR_VEL
            if star.y > SCREEN_H:
                stars.remove(star)
            elif star.y + star.height >= player.y and star.colliderect(player):
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

        draw(player, elapsed_time, stars, hits)

    if is_hit:
        pygame.time.delay(3000)

    pygame.quit()


if __name__ == '__main__':
    main()