from states.state import State


class NewFrameRateState(State):
    def __init__(self, frame_rate=60):
        super().__init__()
        self.frame_rate = frame_rate

    def get_frame_rate(self) -> int:
        return self.frame_rate
