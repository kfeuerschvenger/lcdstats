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
def setup_device(input_handler_instance: InputHandler, screen_manager_instance: ScreenManager, display_type: str = "auto", esp32_host: str = None) -> Device:
    """Set up the display device based on the environment."""
    if display_type == "auto":
        display_type = "raspberry" if IS_RASPBERRY else "window"
    
    if display_type == "raspberry":
        from devices.ILI9163 import ILI9163
        return ILI9163()
    elif display_type == "window":
        import tkinter as tk
        root = tk.Tk()
        input_handler_instance.register_keybinding(root)
        return FakeDisplay(SCREEN_WIDTH, SCREEN_HEIGHT, root)
    elif display_type == "esp32":
        from devices.esp32_wifi_display import ESP32WiFiDisplay
        if not esp32_host:
            raise ValueError("ESP32 host address required for ESP32 display mode")
        
        device = ESP32WiFiDisplay(esp32_host, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        
        # Setup callbacks
        def on_request_next(last_screen: str):
            print(f"ESP32 requested next screen after: {last_screen}")
            screen_manager_instance.handle_button_press()
        
        def on_request_stop():
            print("ESP32 requested stop sending")
            # Could implement stop logic here if needed
        
        device.on_request_next_screen = on_request_next
        device.on_request_stop_sending = on_request_stop
        
        return device
    else:
        raise ValueError(f"Unsupported display type: {display_type}")

# --- Main Loop ---
def main_loop(device: Device, screen_manager: ScreenManager, display_type: str) -> None:
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

        # Update screen ID for ESP32
        if display_type == "esp32":
            screen_id = f"screen{screen_manager.current_index + 1}"
            device.set_screen_id(screen_id)

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
    import argparse
    
    parser = argparse.ArgumentParser(description='LCD Stats Display')
    parser.add_argument('--display', type=str, default='auto', 
                       choices=['auto', 'raspberry', 'window', 'esp32'],
                       help='Display type to use')
    parser.add_argument('--esp32-host', type=str, 
                       help='ESP32 host IP address for WiFi display')
    args = parser.parse_args()

    input_handler_instance = InputHandler(IS_RASPBERRY)
    
    screens: list[Screen] = [
        MainScreen(IS_RASPBERRY, SCREEN_WIDTH, SCREEN_HEIGHT),
        SecondaryScreen(IS_RASPBERRY, SCREEN_WIDTH, SCREEN_HEIGHT)
    ]

    screen_manager = ScreenManager(screens, input_handler_instance)

    device = None
    try:
        device = setup_device(input_handler_instance, screen_manager, args.display, args.esp32_host)
        main_loop(device, screen_manager, args.display)
    except KeyboardInterrupt:
        pass
    finally:
        if device:
            device.clear()
            if args.display == "window":
                device.close()
            elif args.display == "esp32":
                device.close()

if __name__ == "__main__":
    main()