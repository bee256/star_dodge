import sys
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

SCREEN_W, SCREEN_H = (SCREEN.get_width(), SCREEN.get_height())
print(f"Screen size is w: {SCREEN_W}, h: {SCREEN_H}")


def main():
    # Run the game loop
    run = True

    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    # Initial game state is showing the menu
    MenuState.initialise(SCREEN)
    current_state = MenuState()

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
