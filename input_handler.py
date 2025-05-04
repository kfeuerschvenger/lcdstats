import time

class InputHandler:
    LONG_PRESS_THRESHOLD = 3  # seconds
    BUTTON_PIN = 18

    def __init__(self, is_raspberry):
        self.is_raspberry = is_raspberry
        self._short_press_detected = False
        self._long_press_detected = False
        self._long_press_handled = False
        self._pressed_time = None
        self._is_pressed = False
        self._gpio_button = None
        self._window = None

        if self.is_raspberry:
            from periphery import GPIO
            self._gpio_button = GPIO("/dev/gpiochip0", self.BUTTON_PIN, "in", bias="pull_up")

    def register_keybinding(self, window):
        if not self.is_raspberry:
            self._window = window
            self._window.bind("<KeyPress-space>", self._on_key_press)
            self._window.bind("<KeyRelease-space>", self._on_key_release)

    def _on_key_press(self, event):
        if event.keysym == 'space' and not self._is_pressed:
            self._pressed_time = time.time()
            self._is_pressed = True

    def _on_key_release(self, event):
        if event.keysym == 'space' and self._is_pressed:
            self._handle_press_release()
            self._is_pressed = False
            self._pressed_time = None

    def update(self):
        if self.is_raspberry and self._gpio_button:
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

    def _handle_press_release(self):
        press_duration = time.time() - self._pressed_time
        if press_duration >= self.LONG_PRESS_THRESHOLD:
            if not self._long_press_handled:
                self._long_press_detected = True
                self._long_press_handled = True
        else:
            if not self._long_press_handled:
                self._short_press_detected = True

    def was_button_pressed(self):
        was_pressed = self._short_press_detected
        self._short_press_detected = False
        return was_pressed

    def was_long_press(self):
        was_long = self._long_press_detected
        self._long_press_detected = False
        return was_long