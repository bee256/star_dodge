import argparse
import re
import socket


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]
    return all(re.match(r'^[a-zA-Z0-9-]{1,63}$', label) for label in hostname.split("."))


def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def validate_host_or_ip(value):
    if is_valid_hostname(value) or is_valid_ip(value):
        return value
    else:
        raise argparse.ArgumentTypeError(f"Invalid hostname or IP address: {value}")


def validate_port(value):
    port = int(value)
    if 1 <= port <= 65535:
        return port
    else:
        raise argparse.ArgumentTypeError(f"Invalid port number: {value}. Must be between 1 and 65535.")


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
        self.parser.add_argument('-sh', '--score_server_host', type=validate_host_or_ip,
                                 help='Hostname or IP address of the score server to determine the highest score')
        self.parser.add_argument('-sp', '--score_server_port', type=validate_port, help='Port number of the score server', default=8123)
        self.parser.add_argument('-pfr', "--print_frame_rate",
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
