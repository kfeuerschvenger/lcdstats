class Screen:
    def __init__(self, is_raspberry: bool, screen_width: int, screen_height: int):
        self.is_raspberry = is_raspberry
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, delta: float):
        pass

    def draw(self, draw, image):
        pass