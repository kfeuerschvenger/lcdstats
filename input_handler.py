import time

class InputHandler:
    LONG_PRESS_THRESHOLD = 3  # Seconds
    
    def __init__(self, is_raspberry):
        self.is_raspberry = is_raspberry
        self._pressed = False
        self._long_press_detected = False
        self.button_pressed_time = None
        self.is_pressed = False

        if self.is_raspberry:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            self.GPIO = GPIO
            self.BUTTON_PIN = 18
            self.GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        else:
            self.window = None

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
        if self.is_raspberry:
            button_state = self.GPIO.input(self.BUTTON_PIN)
            if button_state == self.GPIO.LOW:
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