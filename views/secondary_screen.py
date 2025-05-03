from PIL import Image
import time
from views.screen import Screen

class SecondaryScreen(Screen):
    # Constants
    DEFAULT_GIF_PATH = "./resources/psyduck.gif"
    DEFAULT_FRAME_DURATION_MS = 100
    MILLISECONDS_IN_SECOND = 1000
    RESIZE_METHOD = Image.NEAREST

    def __init__(self, is_raspberry: bool, screen_width: int, screen_height: int):
        super().__init__(is_raspberry, screen_width, screen_height)

        self.gif_path = self.DEFAULT_GIF_PATH

        self.frames = []
        self.durations = []
        self.current_frame_index = 0
        self.prev_frame_index = 0
        self.last_frame_time = time.time()
        self.draw_position = (0, 0)  # Will be computed after loading the first frame

        self.load_gif()

    def load_gif(self):
        gif = Image.open(self.gif_path)

        try:
            while True:
                frame = gif.copy().convert("RGB")
                resized_frame = frame.resize(
                    (self.screen_width, self.screen_height),
                    self.RESIZE_METHOD
                )
                self.frames.append(resized_frame)
                duration_ms = gif.info.get('duration', self.DEFAULT_FRAME_DURATION_MS)
                duration_s = duration_ms / self.MILLISECONDS_IN_SECOND
                self.durations.append(duration_s)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass  # end of GIF

        if self.frames:
            frame_width, frame_height = self.frames[0].size
            self.draw_position = (
                (self.screen_width - frame_width) // 2,
                (self.screen_height - frame_height) // 2
            )

    def update(self, delta: float):
        current_time = time.time()
        frame_duration = self.durations[self.current_frame_index]

        if current_time - self.last_frame_time >= frame_duration:
            self.prev_frame_index = self.current_frame_index
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.last_frame_time = current_time

    def draw(self, draw, image):
        frame = self.frames[self.current_frame_index]
        prev_frame = self.frames[self.prev_frame_index]

        x, y = self.draw_position

        image.paste(prev_frame, (x, y), prev_frame.convert("L"))
        image.paste(frame, (x, y))