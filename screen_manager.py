class ScreenManager:
    def __init__(self, screens, input_handler_instance):
        self.screens = screens
        self.input_handler = input_handler_instance
        self.current_index = 0
        self.last_index = -1

    def update(self, delta_time):
        if self.input_handler.was_button_pressed():
            self.current_index = (self.current_index + 1) % len(self.screens)

        current_screen = self.screens[self.current_index]

        if self.current_index != self.last_index:
            current_screen.init(current_screen.is_raspberry, current_screen.screen_width, current_screen.screen_height)
            self.last_index = self.current_index

        current_screen.update(delta_time)

    def draw(self, draw, image):
        current_screen = self.screens[self.current_index]
        current_screen.draw(draw, image)