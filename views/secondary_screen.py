from PIL import Image
import time
from views.screen import Screen

class SecondaryScreen(Screen):
    def __init__(self):
        self.gif_path = "./resources/psyduck.gif"
        
        self.is_raspberry = False
        self.screen_width = 0
        self.screen_height = 0
        
        self.target_width = 128
        self.target_height = 128
        self.frames = []
        self.durations = []
        self.current_frame_index = 0
        self.prev_frame_index = 0
        self.last_frame_time = time.time()
        self.screen_width = 128
        self.screen_height = 128

        self.frame_duration = 0.1 # 100ms per frame
        self.target_fps = 10      # For GIFs with variable timing

        self.load_gif()

    def load_gif(self):
        gif = Image.open(self.gif_path)
        try:
            while True:
                frame = gif.copy().convert("RGB")
                resized_frame = frame.resize((self.target_width, self.target_height), Image.NEAREST)
                self.frames.append(resized_frame)
                self.durations.append(gif.info.get('duration', 100) / 1000.0) # in seconds
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass  # gif end

    def init(self, is_raspberry, screen_width, screen_height):
        self.is_raspberry = is_raspberry
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, delta_time):
        current_time = time.time()
        frame_duration = self.durations[self.current_frame_index]

        if current_time - self.last_frame_time >= frame_duration:
            self.prev_frame_index = self.current_frame_index
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.last_frame_time = current_time

    def draw(self, draw, image):
        frame = self.frames[self.current_frame_index]
        prev_frame = self.frames[self.prev_frame_index]

        x = (self.screen_width - self.target_width) // 2
        y = (self.screen_height - self.target_height) // 2

        image.paste(prev_frame, (x, y), prev_frame.convert("L"))
        image.paste(frame, (x, y))