class ScreenManager:
    STARTING_SCREEN = 0

    def __init__(self, screens, input_handler_instance):
        self.screens = screens
        self.input_handler = input_handler_instance
        self.current_index = self.STARTING_SCREEN
        self.last_index = -1
        self.device_on = True

        self.current_screen = self.screens[self.current_index]

    def update(self, delta_time):
        self.input_handler.update()

        if self.input_handler.was_long_press():
            self.device_on = not self.device_on
            if self.device_on:
                self.current_index = self.STARTING_SCREEN
            # print(f"Device {'ON' if self.device_on else 'OFF'}")


        if self.input_handler.was_button_pressed():
            if not self.device_on:
                self.device_on = True
                self.current_index = self.STARTING_SCREEN
                # print("Device ON")
            else:
                self.current_index = (self.current_index + 1) % len(self.screens)

        self.current_screen = self.screens[self.current_index]

        if self.current_index != self.last_index:
            self.current_screen.init(self.current_screen.is_raspberry, self.current_screen.screen_width, self.current_screen.screen_height)
            self.last_index = self.current_index

        self.current_screen.update(delta_time)

    def draw(self, draw, image):
        if not self.device_on:
            draw.rectangle((0, 0, self.current_screen.screen_width, self.current_screen.screen_height), fill=(0, 0, 0))
            return

        self.current_screen.draw(draw, image)