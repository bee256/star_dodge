import argparse


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-w", "--window", nargs='*', type=int, dest="window",
                                 help="Run game in window mode. Default 1200x800 pixels. You may optionally provide two integer arguments to change the window size.")
        self.parser.add_argument("-v", "--verbose", help="Write output to console",
                                 action="store_true")
        self.parser.add_argument("--print_frame_rate",
                                 help="Print the frame rate of the game every 5 seconds",
                                 action="store_true")
        self.parser.add_argument("--store_time_num_stars_csv",
                                 help="Stores a csv file to show how stars are created over time. This helps to optimise the game logic.",
                                 action="store_true")
        self.args = self.parser.parse_args()

    def get_arg(self, arg_name):
        return getattr(self.args, arg_name, None)


# Usage example
if __name__ == "__main__":
    config = Config()
    example_arg = config.get_arg('example')
    number_arg = config.get_arg('number')
    print(f"Example argument: {example_arg}")
    print(f"Number argument: {number_arg}")

    # You can now access these arguments in other classes or functions
    class AnotherClass:
        def __init__(self):
            self.example = config.get_arg('example')
            self.number = config.get_arg('number')

        def display_args(self):
            print(f"In AnotherClass - Example: {self.example}, Number: {self.number}")


    another_instance = AnotherClass()
    another_instance.display_args()
