from PIL import Image, ImageDraw

from views.screen import Screen
from input_handler import InputHandler
from utils.progress_indicator import ProgressIndicator

class ScreenManager:
    STARTING_SCREEN_INDEX = 0 # The index of the starting screen

    def __init__(self, screens: list[Screen], input_handler: InputHandler) -> None:
        """Initialize the ScreenManager with a list of screens and an input handler."""
        self.screens = screens
        self.input_handler = input_handler
        self.current_index = self.STARTING_SCREEN_INDEX
        self.last_index = -1
        self.device_on = True
        self.current_press_duration = 0.0
        self.current_screen = self.screens[self.current_index]

        self.progress_indicator = ProgressIndicator()

    def update(self, delta: float) -> None:
        """Update the current screen and handle input events."""
        self.input_handler.update()
        self.current_press_duration = self.input_handler.get_current_press_duration()

        if self.input_handler.was_long_press():
            self.toggle_device_state()

        if self.input_handler.was_button_pressed():
            self.handle_button_press()

        self.switch_screen_if_needed()
        self.current_screen.update(delta)

    def _draw_progress(self, image: Image.Image) -> None:
        """Dibuja el indicador de progreso usando la clase dedicada."""
        self.progress_indicator.draw(
            base_image=image,
            elapsed_time=self.current_press_duration,
            max_time=InputHandler.LONG_PRESS_THRESHOLD
        )

    def draw(self, draw: ImageDraw.ImageDraw, image: Image.Image) -> None:
        """Draw the on the current screen."""
        if not self.device_on:
            draw.rectangle((0, 0, self.current_screen.screen_width, self.current_screen.screen_height), fill='black')
            return

        self.current_screen.draw(draw, image)
        self._draw_progress(image)

    def toggle_device_state(self) -> None:
        """Toggle the device state between on and off."""
        self.device_on = not self.device_on
        self.current_press_duration = 0.0
        self.input_handler.reset_press_state()
        if self.device_on:
            self.current_index = self.STARTING_SCREEN_INDEX
        self.last_index = -1

    def handle_button_press(self) -> None:
        """Handle button press event."""
        if not self.device_on:
            self.device_on = True
            self.current_index = self.STARTING_SCREEN_INDEX
            self.current_press_duration = 0.0
        else:
            if not self.input_handler.was_long_press():
                self.current_index = (self.current_index + 1) % len(self.screens)

    def switch_screen_if_needed(self) -> None:
        """Switch to the next screen if the current index has changed."""
        if self.current_index != self.last_index:
            screen = self.screens[self.current_index]
            self.last_index = self.current_index
            self.current_screen = screen