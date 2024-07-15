import os
from os import path
import platform

# This base directory works for the pyinstaller bundled script as well as the non-bundled one.
# See as well https://pyinstaller.org/en/stable/runtime-information.html
# We call path.dirname() twice, as the first call will give the location of paths.py which is not wat we want
# as it will have the path of utils at the end. So to go up one dir level we call dirname again.
base_dir = path.dirname(path.abspath(path.dirname(__file__)))
# print(f"{__name__} base_dir is: {base_dir}")

dir_sound = path.join(base_dir, 'assets', 'sound')
dir_fonts = path.join(base_dir, 'assets', 'fonts')
dir_images = path.join(base_dir, 'assets', 'images')


def get_data_dir():
    system = platform.system()
    if system == 'Windows':
        data_dir = os.getenv('LOCALAPPDATA')
    elif system == 'Darwin':  # macOS
        data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    else:  # Linux and other UNIX-like systems
        data_dir = os.path.join(os.path.expanduser('~'), '.local', 'share')
    data_dir = os.path.join(data_dir, 'StarDodge')
    return data_dir


def get_highscore_path():
    os.makedirs(get_data_dir(), exist_ok=True)
    highscore_path = os.path.join(get_data_dir(), 'highscores.csv')
    return highscore_path
