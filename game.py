import sys

from game_states import *

pg.init()
pg.font.init()
arguments = sys.argv[1:]
if len(arguments) > 0 and arguments[0].find('window'):
    # Work in windowed mode
    WIN = pg.display.set_mode((1200, 800))
else:
    # Set display mode to full-screen
    WIN = pg.display.set_mode((0, 0), pg.FULLSCREEN)

info_display = pg.display.Info()
SCREEN_W, SCREEN_H = (info_display.current_w, info_display.current_h)
print(f"Screen w: {SCREEN_W}, h: {SCREEN_H}")

BG_IMG = pg.transform.scale(pg.image.load(path.join('assets', 'images', 'background.jpeg')), (SCREEN_W, SCREEN_H))

FONT_SIZE_BASE = int(SCREEN_H / 25)
SHIP_VEL = 5
STARS_CREATE_PER_INCREMENT = 4

TIME_FONT = pg.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), FONT_SIZE_BASE)
LOST_FONT = pg.font.Font(path.join('assets', 'fonts', 'StarJedi-DGRW.ttf'), FONT_SIZE_BASE * 2)
SOUND_CRASH = pg.mixer.Sound(path.join('assets', 'sound', 'rubble_crash.wav'))
SOUND_HIT = pg.mixer.Sound(path.join('assets', 'sound', 'metal_trash_can_filled_2.wav'))
pg.mixer.music.load(path.join('assets', 'sound', 'planetary_paths.mp3'), 'planet_paths')
HITS_MAX = 3


def main():
    # Run the game loop
    run = True

    clock = pg.time.Clock()
    # print(f"Framerate: {clock.get_fps():.2f}")

    pg.mouse.set_visible(False)

    # Initial state
    current_state = MenuState(WIN, running_game=None)

    while run:
        frame_time = clock.tick(60)
        # clock_tick_num_calls += 1
        # if clock_tick_num_calls == 50:
        #     print(f"Framerate: {clock.get_fps():.2f}")
        #     clock_tick_num_calls = 0

        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False
                break

        # Handle events, and render based on the current state
        new_state = current_state.handle_events(events, frame_time)
        if new_state:
            if type(new_state) is QuitState:
                break
            current_state = new_state

        current_state.render()
        pg.display.flip()

    # end of game loop

    pg.quit()


if __name__ == '__main__':
    main()
