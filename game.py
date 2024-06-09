import sys
# import time
import pygame as pg
from states.menu_state import MenuState
from states.quit_state import QuitState

pg.init()
pg.font.init()
arguments = sys.argv[1:]
if len(arguments) > 0 and arguments[0].find('window') >= 0:
    # Work in windowed mode
    SCREEN = pg.display.set_mode((1200, 800))
else:
    # Set display mode to full screen
    SCREEN = pg.display.set_mode((0, 0), pg.FULLSCREEN)

print(f"Screen size is w: {SCREEN.get_width()}, h: {SCREEN.get_height()}")


def main():
    # Run the game loop
    run = True

    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    # Initial game state is showing the menu
    MenuState.initialise(SCREEN)
    current_state = MenuState()
    frame_rate = current_state.get_frame_rate()
    # last_frame_rate_print = time.time()

    while run:
        frame_time = clock.tick(frame_rate)
        # if time.time() - last_frame_rate_print >= 5.0:
        #     print(f"Framerate last 5 secs: {clock.get_fps():.2f}")
        #     last_frame_rate_print = time.time()

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
            frame_rate = new_state.get_frame_rate()

        current_state.render()
        pg.display.flip()
        # end of game loop

    pg.quit()


if __name__ == '__main__':
    main()
