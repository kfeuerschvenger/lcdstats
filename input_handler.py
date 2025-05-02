import time

class InputHandler:
    LONG_PRESS_THRESHOLD = 3  # Seconds
    BUTTON_PIN = 18
    
    def __init__(self, is_raspberry):
        self.is_raspberry = is_raspberry
        self._pressed = False
        self._long_press_detected = False
        self.button_pressed_time = None
        self.is_pressed = False
        self.button_gpio = None

        if self.is_raspberry:
            from periphery import GPIO
            self.button_gpio = GPIO("/dev/gpiochip0", self.BUTTON_PIN, "in", bias="pull_up")

    def register_keybinding(self, window):
        if not self.is_raspberry:
            self.window = window
            self.window.bind("<KeyPress-space>", self.on_key_press)
            self.window.bind("<KeyRelease-space>", self.on_key_release)

    def on_key_press(self, event):
        if event.keysym == 'space':
            if not self.is_pressed:
                self.button_pressed_time = time.time()
                self.is_pressed = True

    def on_key_release(self, event):
        if event.keysym == 'space':
            if self.is_pressed:
                if self.button_pressed_time is not None:
                    press_duration = time.time() - self.button_pressed_time
                    if press_duration >= self.LONG_PRESS_THRESHOLD:
                        self._long_press_detected = True
                    else:
                        self._pressed = True
                self.button_pressed_time = None
                self.is_pressed = False

    def update(self):
        if self.is_raspberry and self.button_gpio:
            button_state = self.button_gpio.read()
            
            if not button_state:
                if self.button_pressed_time is None:
                    self.button_pressed_time = time.time()
                else:
                    press_duration = time.time() - self.button_pressed_time
                    if press_duration >= self.LONG_PRESS_THRESHOLD:
                        self._long_press_detected = True
            else:
                if self.button_pressed_time is not None:
                    press_duration = time.time() - self.button_pressed_time
                    if press_duration < self.LONG_PRESS_THRESHOLD:
                        self._pressed = True
                    self.button_pressed_time = None

    def was_button_pressed(self):
        result = self._pressed
        self._pressed = False
        return result

    def was_long_press(self):
        result = self._long_press_detected
        self._long_press_detected = False
        return result