from PIL import Image

class Device:
    """This class defines the interface for devices that can display images."""
    
    def __init__(self, width: int, height: int) -> None:
        """Initialize the device with a given width and height."""
        self.width = width
        self.height = height

    def update(self) -> None:
        """This method should be overridden by subclasses."""
        pass

    def display(self, image: Image.Image) -> None:
        """This method should be overridden by subclasses."""
        pass

    def clear(self) -> None:
        """This method should be overridden by subclasses."""
        pass

    def close(self) -> None:
        """This method should be overridden by subclasses."""
        pass