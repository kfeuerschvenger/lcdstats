class ScreenManager:
    STARTING_SCREEN_INDEX = 0

    def __init__(self, screens, input_handler):
        self.screens = screens
        self.input_handler = input_handler
        self.current_index = self.STARTING_SCREEN_INDEX
        self.last_index = -1
        self.device_on = True
        self.current_screen = self.screens[self.current_index]

    def update(self, delta: float):
        self.input_handler.update()

        if self.input_handler.was_long_press():
            self.toggle_device_state()

        if self.input_handler.was_button_pressed():
            self.handle_button_press()

        self.switch_screen_if_needed()
        self.current_screen.update(delta)

    def draw(self, draw, image):
        if not self.device_on:
            draw.rectangle((0, 0, self.current_screen.screen_width, self.current_screen.screen_height), fill='black')
            return

        self.current_screen.draw(draw, image)

    def toggle_device_state(self):
        self.device_on = not self.device_on
        if self.device_on:
            self.current_index = self.STARTING_SCREEN_INDEX

    def handle_button_press(self):
        if not self.device_on:
            self.device_on = True
            self.current_index = self.STARTING_SCREEN_INDEX
        else:
            self.current_index = (self.current_index + 1) % len(self.screens)

    def switch_screen_if_needed(self):
        if self.current_index != self.last_index:
            screen = self.screens[self.current_index]
            self.last_index = self.current_index
            self.current_screen = screen