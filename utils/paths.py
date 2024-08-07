import os
from os import path
import platform
import re

# This base directory works for the pyinstaller bundled script as well as the non-bundled one.
# See as well https://pyinstaller.org/en/stable/runtime-information.html
# We call path.dirname() twice, as the first call will give the location of paths.py which is not wat we want
# as it will have the path of utils at the end. So to go up one dir level we call dirname again.
base_dir = path.dirname(path.abspath(path.dirname(__file__)))
# print(f"{__name__} base_dir is: {base_dir}")

dir_sound = path.join(base_dir, 'assets', 'sound')
dir_fonts = path.join(base_dir, 'assets', 'fonts')
dir_images = path.join(base_dir, 'assets', 'images')
dir_data_no_git = path.join(base_dir, 'data_no_git')


def get_data_dir():
    system = platform.system()
    if system == 'Windows':
        data_dir = os.getenv('LOCALAPPDATA')
    elif system == 'Darwin':  # macOS
        data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    else:  # Linux and other UNIX-like systems
        data_dir = os.path.join(os.path.expanduser('~'), '.local', 'share')
    data_dir = os.path.join(data_dir, 'StarDodge')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_highscore_path():
    highscore_path = os.path.join(get_data_dir(), 'highscores.csv')
    return highscore_path


def sanitize_filename(filename):
    # Define a pattern for characters that are not allowed in filenames.
    # Space would be OK, but we replace it by _ as well.
    invalid_chars = r'[\\/:*?"<>| ]'
    # Replace these characters with an underscore
    sanitized_filename = re.sub(invalid_chars, '_', filename)
    return sanitized_filename
