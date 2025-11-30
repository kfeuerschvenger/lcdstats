import time

class InputHandler:
    LONG_PRESS_THRESHOLD = 3  # seconds
    BUTTON_PIN = 18 # GPIO pin number for the button (BCM numbering)

    def __init__(self, is_raspberry: bool = True, use_gpio: bool = True) -> None:
        """
        Initialize the InputHandler.

        Args:
            is_raspberry: Whether running on Raspberry Pi
            use_gpio: Whether to use GPIO (False for ESP32 WiFi mode)
        """
        self.is_raspberry = is_raspberry
        self.use_gpio = use_gpio  # Only use GPIO for native LCD mode
        self._short_press_detected = False
        self._long_press_detected = False
        self._long_press_handled = False
        self._pressed_time = None
        self._is_pressed = False
        self._gpio_button = None
        self._window = None

        # Only initialize GPIO if we're in native Raspberry Pi mode with GPIO
        if self.is_raspberry and self.use_gpio:
            try:
                from periphery import GPIO
                self._gpio_button = GPIO("/dev/gpiochip0", self.BUTTON_PIN, "in", bias="pull_up")
                print("GPIO initialized for button input")
            except Exception as e:
                print(f"GPIO initialization failed: {e}")
                print("  Continuing without GPIO (button input disabled)")
                self._gpio_button = None
                self.use_gpio = False

    def register_keybinding(self, window) -> None:
        """Register keybinding for space key press and release events."""
        if not self.is_raspberry:
            self._window = window
            self._window.bind("<KeyPress-space>", self._on_key_press)
            self._window.bind("<KeyRelease-space>", self._on_key_release)

    def _on_key_press(self, event) -> None:
        """Handle key press event."""
        if event.keysym == 'space' and not self._is_pressed:
            self._pressed_time = time.time()
            self._is_pressed = True
            self._long_press_handled = False

    def _on_key_release(self, event) -> None:
        """Handle key release event."""
        if event.keysym == 'space' and self._is_pressed:
            press_duration = time.time() - (self._pressed_time or 0)
            self._is_pressed = False
            self._pressed_time = None

            if press_duration >= self.LONG_PRESS_THRESHOLD:
                if not self._long_press_handled:
                    self._long_press_detected = True
            else:
                self._short_press_detected = True

            self._long_press_handled = False

    def update(self) -> None:
        """Update the button state and check for long/short press."""

        if not self._is_pressed:
            self._pressed_time = None
            self._long_press_handled = False

        # Handle Tkinter window events
        if not self.is_raspberry and self._window:
            self._window.update()

        # Handle GPIO button (only if GPIO is enabled)
        if self.is_raspberry and self.use_gpio and self._gpio_button:
            button_state = self._gpio_button.read()

            if not button_state:  # Button pressed (active low)
                if self._pressed_time is None:
                    self._pressed_time = time.time()
                    self._long_press_handled = False
                elif not self._long_press_handled and time.time() - self._pressed_time >= self.LONG_PRESS_THRESHOLD:
                    self._long_press_detected = True
                    self._long_press_handled = True
            elif self._pressed_time is not None:
                self._handle_press_release()
                self._pressed_time = None

    def _handle_press_release(self) -> None:
        """Handle the button press and release event."""
        press_duration = time.time() - (self._pressed_time or 0)
        if press_duration >= self.LONG_PRESS_THRESHOLD:
            if not self._long_press_handled:
                self._long_press_detected = True
                self._long_press_handled = True
        else:
            if not self._long_press_handled:
                self._short_press_detected = True

    def was_button_pressed(self) -> bool:
        """Check if the button was pressed."""
        was_pressed = self._short_press_detected
        self._short_press_detected = False
        return was_pressed

    def was_long_press(self) -> bool:
        """Check if a long press was detected."""
        was_long = self._long_press_detected
        self._long_press_detected = False
        return was_long

    def get_current_press_duration(self) -> float:
        """Get the duration of the current press. 0 if not pressed."""
        if self._pressed_time is None:
            return 0.0
        return time.time() - self._pressed_time

    def is_button_pressed(self) -> bool:
        """Check if the button is currently pressed."""
        return self._is_pressed

    def reset_press_state(self) -> None:
        """Reset the all button press states."""
        self._pressed_time = None
        self._short_press_detected = False
        self._long_press_detected = False
        self._long_press_handled = False
        self._is_pressed = False