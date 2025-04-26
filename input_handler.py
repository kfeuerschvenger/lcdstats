class InputHandler:
    def __init__(self, is_raspberry):
        self.is_raspberry = is_raspberry
        self._pressed = False

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
            self.window.bind("<Key>", self.on_key_press)

    def on_key_press(self, event):
        if event.keysym == 'space':
            self._pressed = True

    def was_button_pressed(self):
        if self.is_raspberry:
            return self.GPIO.input(self.BUTTON_PIN) == self.GPIO.LOW
        else:
            result = self._pressed
            self._pressed = False
            return result