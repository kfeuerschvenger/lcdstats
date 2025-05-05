import platform
import time
from PIL import Image, ImageDraw

from devices.device import Device
from devices.fake_display import FakeDisplay
from screen_manager import ScreenManager
from views.screen import Screen
from views.main_screen import MainScreen
from views.secondary_screen import SecondaryScreen
from input_handler import InputHandler

# --- Screen config ---
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 128
SCREEN_ROTATE = 0

FPS = 30
FRAME_DURATION = 1 / FPS

# --- Environment Check ---
def is_raspberry_pi() -> bool:
    """Check if the current platform is a Raspberry Pi."""
    if platform.system() != "Linux":
        return False
    machine = platform.uname().machine
    return machine.startswith(('arm', 'aarch', 'rpi'))

IS_RASPBERRY = is_raspberry_pi()

# --- Device Setup ---
def setup_device(input_handler_instance: InputHandler) -> Device:
    """Set up the display device based on the environment."""
    if IS_RASPBERRY:
        from devices.ILI9163 import ILI9163
        return ILI9163()
    else:
        import tkinter as tk
        root = tk.Tk()
        input_handler_instance.register_keybinding(root)
        return FakeDisplay(SCREEN_WIDTH, SCREEN_HEIGHT, root)

# --- Main Loop ---
def main_loop(device: Device, screen_manager: ScreenManager) -> None:
    """Main loop for the application."""
    last_frame_time = time.monotonic()

    while True:
        # Limit frame rate
        now = time.monotonic()
        elapsed = now - last_frame_time
        if elapsed < FRAME_DURATION:
            time.sleep(FRAME_DURATION - elapsed)
        current_time = time.monotonic()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time

        # Prepare frame
        frame = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)

        # Update and draw current screen
        screen_manager.update(delta_time)
        screen_manager.draw(draw, frame)

        # Render to display
        if not IS_RASPBERRY:
            base = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 255))
            final_image = Image.alpha_composite(base, frame)
            device.display(final_image)
        else:
            device.display(frame)

        if not IS_RASPBERRY:
            device.update()

# --- Entry Point ---
def main() -> None:
    """Main entry point for the application."""
    input_handler_instance = InputHandler(IS_RASPBERRY)
    
    screens: list[Screen] = [
        MainScreen(IS_RASPBERRY, SCREEN_WIDTH, SCREEN_HEIGHT),
        SecondaryScreen(IS_RASPBERRY, SCREEN_WIDTH, SCREEN_HEIGHT)
    ]

    screen_manager = ScreenManager(screens, input_handler_instance)

    device = None
    try:
        device = setup_device(input_handler_instance)
        main_loop(device, screen_manager)
    except KeyboardInterrupt:
        pass
    finally:
        if device:
            device.clear()
            if not IS_RASPBERRY:
                device.close()

if __name__ == "__main__":
    main()