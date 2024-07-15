# base colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
# additional colors
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIGHT_BLUE = (0, 160, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)
DARK_RED = (200, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 182, 193)



# Q: What are typical ranges of RGB values of the colors of stars?
#
# ChatGPT: Stars display a wide range of colors based on their temperature, which can be represented by RGB values. Here are typical ranges for the colors of stars:
#
# 1. **Blue Stars (Hottest)**
#    - Temperature: 25,000 - 50,000 K
#    - RGB Range: (150, 200, 255) to (220, 240, 255)
#
# 2. **Blue-White Stars**
#    - Temperature: 10,000 - 25,000 K
#    - RGB Range: (170, 190, 255) to (200, 220, 255)
#
# 3. **White Stars**
#    - Temperature: 7,500 - 10,000 K
#    - RGB Range: (230, 230, 255) to (255, 255, 255)
#
# 4. **Yellow-White Stars**
#    - Temperature: 6,000 - 7,500 K
#    - RGB Range: (255, 250, 210) to (255, 255, 240)
#
# 5. **Yellow Stars**
#    - Temperature: 5,000 - 6,000 K
#    - RGB Range: (255, 245, 160) to (255, 250, 200)
#
# 6. **Orange Stars**
#    - Temperature: 3,500 - 5,000 K
#    - RGB Range: (255, 200, 100) to (255, 230, 180)
#
# 7. **Red Stars (Coolest)**
#    - Temperature: 2,500 - 3,500 K
#    - RGB Range: (255, 100, 50) to (255, 150, 100)
#
# These ranges are approximate and can vary depending on the specific characteristics and composition of each star.
#
#
# Q: OK, and can you give me some python code which implements thee color ranges?
#
# ChatGPT: Sure! Here is a Python code snippet that implements the typical RGB color ranges for different types of stars:
#
# # Define a dictionary with star types and their corresponding RGB ranges
# star_colors = {
#     "Blue": {"temperature_range": (25000, 50000), "rgb_range": ((150, 200, 255), (220, 240, 255))},
#     "Blue-White": {"temperature_range": (10000, 25000), "rgb_range": ((170, 190, 255), (200, 220, 255))},
#     "White": {"temperature_range": (7500, 10000), "rgb_range": ((230, 230, 255), (255, 255, 255))},
#     "Yellow-White": {"temperature_range": (6000, 7500), "rgb_range": ((255, 250, 210), (255, 255, 240))},
#     "Yellow": {"temperature_range": (5000, 6000), "rgb_range": ((255, 245, 160), (255, 250, 200))},
#     "Orange": {"temperature_range": (3500, 5000), "rgb_range": ((255, 200, 100), (255, 230, 180))},
#     "Red": {"temperature_range": (2500, 3500), "rgb_range": ((255, 100, 50), (255, 150, 100))}
# }
#
# def display_star_colors():
#     for star_type, properties in star_colors.items():
#         temp_range = properties["temperature_range"]
#         rgb_range = properties["rgb_range"]
#         print(f"{star_type} Stars:")
#         print(f"  Temperature Range: {temp_range[0]} K - {temp_range[1]} K")
#         print(f"  RGB Range: {rgb_range[0]} to {rgb_range[1]}\n")
#
# # Display the star color ranges
# display_star_colors()
#
# This script defines a dictionary star_colors with the star types as keys. Each star type maps to a dictionary containing the
# temperature range and the corresponding RGB range. The display_star_colors function iterates through the dictionary
# and prints out the information for each star type. You can run this script to see the typical ranges of RGB values for the colors of stars.
#
#
# Q: OK, but I want to have random colors in the specific range
#
# ChatGPT: To generate random colors within the specific RGB ranges for different types of stars, you can use the following Python code:
#
#     import random
#
#     # Define a dictionary with star types and their corresponding RGB ranges
#     star_colors = {
#         "Blue": {"temperature_range": (25000, 50000), "rgb_range": ((150, 200, 255), (220, 240, 255))},
#         "Blue-White": {"temperature_range": (10000, 25000), "rgb_range": ((170, 190, 255), (200, 220, 255))},
#         "White": {"temperature_range": (7500, 10000), "rgb_range": ((230, 230, 255), (255, 255, 255))},
#         "Yellow-White": {"temperature_range": (6000, 7500), "rgb_range": ((255, 250, 210), (255, 255, 240))},
#         "Yellow": {"temperature_range": (5000, 6000), "rgb_range": ((255, 245, 160), (255, 250, 200))},
#         "Orange": {"temperature_range": (3500, 5000), "rgb_range": ((255, 200, 100), (255, 230, 180))},
#         "Red": {"temperature_range": (2500, 3500), "rgb_range": ((255, 100, 50), (255, 150, 100))}
#     }
#
#
#     def generate_random_rgb(star_type):
#         if star_type not in star_colors:
#             raise ValueError("Invalid star type. Choose from: " + ", ".join(star_colors.keys()))
#
#         rgb_range = star_colors[star_type]["rgb_range"]
#         r = random.randint(rgb_range[0][0], rgb_range[1][0])
#         g = random.randint(rgb_range[0][1], rgb_range[1][1])
#         b = random.randint(rgb_range[0][2], rgb_range[1][2])
#
#         return (r, g, b)
#
#
#     # Example usage:
#     for star_type in star_colors.keys():
#         random_rgb = generate_random_rgb(star_type)
#         print(f"{star_type} Star Random RGB: {random_rgb}")
#
# This script includes a function generate_random_rgb that takes a star type as an input and returns a random RGB value within
# the specified range for that star type. The random.randint function is used to generate random values within the specified RGB ranges.
# The example usage demonstrates how to generate and print random RGB values for each star type.
