from os import path

# This base directory works for the pyinstaller bundled script as well as the non-bundled one.
# See as well https://pyinstaller.org/en/stable/runtime-information.html
# We call path.dirname() twice, as the first call will give the location of paths.py which is not wat we want
# as it will have the path of utils at the end. So to go up one dir level we call dirname again.
base_dir = path.dirname(path.abspath(path.dirname(__file__)))
# print(f"{__name__} base_dir is: {base_dir}")

dir_sound = path.join(base_dir, 'assets', 'sound')
dir_fonts = path.join(base_dir, 'assets', 'fonts')
dir_images = path.join(base_dir, 'assets', 'images')
