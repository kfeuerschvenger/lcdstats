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

LOOPTIME = 0.05

# --- Check if Raspberry Pi ---
is_raspberry = platform.system() == "Linux" and os.uname().machine.startswith('arm')

input_handler_instance = input_handler.InputHandler(is_raspberry)

screens = [MainScreen(), SecondaryScreen()]
manager = ScreenManager(screens, input_handler_instance)

# --- Device Setup ---
def setup_device():
    if is_raspberry:
        import luma.lcd.device as lcd_device
        import luma.core.interface.serial as lcd_serial
        serial = lcd_serial.spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
        # My LCD DRIVE IC is ILI9163, you may need to change this to ST7735 or whatever you need.
        device = lcd_device.ili9163(serial_interface=serial, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, rotate=SCREEN_ROTATE, bgr=True)
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
    last_time = time.time()
    
    manager.screens[manager.current_index].init(is_raspberry, SCREEN_WIDTH, SCREEN_HEIGHT)
    manager.screens[manager.current_index].update(0)
    manager.screens[manager.current_index].draw(draw, image)

    while True:
        current_time = time.time()
        delta = current_time - last_time
        last_time = current_time

        manager.update(delta)
        manager.draw(draw, image)

        device.display(image)
        if not is_raspberry:
            device.update()

        time.sleep(LOOPTIME)

# --- Start Program ---
if __name__ == "__main__":
    try:
        device = setup_device()
        main_loop(device)
    except KeyboardInterrupt:
        pass
    finally:
        if is_raspberry:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
            device.clear()
        else:
            device.clear()
            device.close()