import os
import platform
import time
from PIL import Image, ImageDraw
from fake_display import FakeDisplay
import input_handler
from screen_manager import ScreenManager
from views.main_screen import MainScreen
from views.secondary_screen import SecondaryScreen

# --- Screen config ---
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 128
SCREEN_ROTATE = 0

LOOPTIME = 1/30  # 30 FPS max

# --- Check if Raspberry Pi ---
is_raspberry = platform.system() == "Linux" and (
    os.uname().machine.startswith('arm') 
    or os.uname().machine.startswith('aarch')
    or os.uname().machine.startswith('rpi')
)

input_handler_instance = input_handler.InputHandler(is_raspberry)

screens = [MainScreen(), SecondaryScreen()]
manager = ScreenManager(screens, input_handler_instance)

# --- Device Setup ---
def setup_device():
    if is_raspberry:
        from ILI9163 import ILI9163
        device = ILI9163()
    else:
        import tkinter as tk
        root = tk.Tk()
        input_handler_instance.register_keybinding(root)
        device = FakeDisplay(SCREEN_WIDTH, SCREEN_HEIGHT, root)
    return device

# Create a blank image for drawing
image = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0))
# Get drawing object to draw on image
draw = ImageDraw.Draw(image)

# --- Main Render Function ---
def main_loop(device):
    last_vsync = time.monotonic()
    last_frame_time = time.monotonic()

    while True:
        while (time.monotonic() - last_vsync) < LOOPTIME:
            time.sleep(0.001)
        last_vsync = time.monotonic()

        current_time = time.monotonic()
        delta = current_time - last_frame_time
        last_frame_time = current_time

        image = Image.new('RGB', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        manager.update(delta)
        manager.draw(draw, image)

        device.display(image)
        if not is_raspberry:
            device.update()

# --- Start Program ---
if __name__ == "__main__":
    device = None
    try:
        device = setup_device()
        main_loop(device)
    except KeyboardInterrupt:
        pass
    finally:
        if device:
            if is_raspberry:
                device.clear()
            else:
                device.clear()
                device.close()