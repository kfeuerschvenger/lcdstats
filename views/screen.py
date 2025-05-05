from PIL import Image, ImageDraw

class Screen:
    """Base class for screens in the application."""

    def __init__(self, is_raspberry: bool, screen_width: int, screen_height: int) -> None:
        """Initialize the screen with the given parameters."""
        self.is_raspberry = is_raspberry
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, delta: float) -> None:
        """Update the screen. This method should be overridden by subclasses."""
        pass

    def draw(self, draw: ImageDraw.ImageDraw, image: Image.Image) -> None:
        """Draw the screen. This method should be overridden by subclasses."""
        pass