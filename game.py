import os
import time
import asyncio
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg

from utils.config import Config
from utils.settings import Settings
from states.menu_state import MenuState
from states.quit_state import QuitState
from states.new_frame_rate_state import NewFrameRateState


async def main():
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
        elif len(arg_win) == 1:
            (width, height) = (arg_win[0], round(arg_win[0] * 9 / 16))
        screen = pg.display.set_mode((width, height))

    # Now we have the screen, we can init the Settings() singleton class and give the screen for the first call.
    Settings(screen)
    if config.get_arg('verbose'):
        print(f"Screen size is w: {screen.get_width()}, h: {screen.get_height()}")

    # Run the game loop
    run = True

    clock = pg.time.Clock()
    pg.mouse.set_visible(False)

    # Initial game state is showing the menu
    current_state = MenuState()
    frame_rate = current_state.get_frame_rate()
    last_frame_rate_print = time.time()

    while run:
        frame_time = clock.tick(frame_rate)
        if arg_print_frame_rate:
            if time.time() - last_frame_rate_print >= 5.0:
                print(f"Framerate last 5 secs: {clock.get_fps():.2f}")
                last_frame_rate_print = time.time()

        await asyncio.sleep(0)  # Yield control to the asyncio event loop

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
            elif type(new_state) is NewFrameRateState:
                pass
            else:
                current_state = new_state
            frame_rate = new_state.get_frame_rate()

        current_state.render()
        pg.display.flip()
        # end of game loop

    pg.quit()


if __name__ == '__main__':
    asyncio.run(main())
