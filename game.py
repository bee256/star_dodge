import time
import pygame as pg

from utils.config import Config
from states.state import State
from states.menu_state import MenuState
from states.quit_state import QuitState

def main():
    pg.init()
    pg.font.init()

    config = Config()
    arg_win = config.get_arg('window')
    arg_print_frame_rate = config.get_arg('print_frame_rate')

    if arg_win is None:
        # Set display mode to full screen
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    else:
        # Work in windowed mode
        (width, height) = (1200, 800)
        if len(arg_win) == 2:
            (width, height) = (arg_win[0], arg_win[1])
        screen = pg.display.set_mode((width, height))

    if config.get_arg('verbose'):
        print(f"Screen size is w: {screen.get_width()}, h: {screen.get_height()}")

    # Run the game loop
    run = True

    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    State(screen)
    # Initial game state is showing the menu
    MenuState.initialise()
    current_state = MenuState()
    frame_rate = current_state.get_frame_rate()
    last_frame_rate_print = time.time()

    while run:
        frame_time = clock.tick(frame_rate)
        if arg_print_frame_rate:
            if time.time() - last_frame_rate_print >= 5.0:
                print(f"Framerate last 5 secs: {clock.get_fps():.2f}")
                last_frame_rate_print = time.time()

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
