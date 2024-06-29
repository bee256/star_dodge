class State:
    def handle_events(self, events, frame_time):
        raise NotImplementedError("Subclass must implement abstract method")

    def render(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_frame_rate(self) -> int:
        # Classes derived from State class are supposed to overwrite this method to return a reasonable frame rate
        return 60
