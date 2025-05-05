import tkinter as tk
from PIL import ImageTk, Image

from devices.device import Device

# Constants
SCALE_FACTOR = 2  # Scale the canvas for better visibility in simulation
BACKGROUND_COLOR = "#FFFFFF"  # Background color of the canvas
CLEAR_COLOR = (0, 0, 0)  # RGB color used when clearing the screen

class FakeDisplay(Device):
    def __init__(self, width: int, height: int, root: tk.Tk):
        super().__init__(width, height)
        self.root = root
        self.closed = False
        self.root.title("Fake LCD Display")

        # Create a canvas with scaled size for better visibility
        self.canvas = tk.Canvas(
            self.root,
            width=width * SCALE_FACTOR,
            height=height * SCALE_FACTOR,
            bg=BACKGROUND_COLOR,
            highlightthickness=0
        )
        self.canvas.pack()
        self.tk_image = None
        self.alpha_bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    def display(self, image: Image.Image):
        """Display the given PIL image on the canvas."""
        if self.closed:
            return

        try:
            if not self.root.winfo_exists():
                self.closed = True
                return
        except tk.TclError:
            self.closed = True
            return

        try:
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            composite = Image.alpha_composite(self.alpha_bg, image)
            rgb_image = composite.convert("RGB")

            scaled_image = rgb_image.resize((self.width, self.height), Image.NEAREST)

            self.tk_image = ImageTk.PhotoImage(scaled_image)
            self.canvas.create_image(self.width // 2, self.height // 2, anchor=tk.NW, image=self.tk_image)
        except tk.TclError:
            self.closed = True

    def clear(self):
        """Clear the display by filling it with black."""
        if not self.closed:
            try:
                self.display(Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0)))
            except tk.TclError:
                self.closed = True

    def update(self) -> None:
        """Update the Tkinter event loop."""
        if self.closed:
            return
        try:
            self.root.update_idletasks()
            self.root.update()
        except tk.TclError:
            self.closed = True

    def close(self):
        """Close the Tkinter window."""
        if not self.closed:
            try:
                self.root.destroy()
            except tk.TclError:
                pass
            self.closed = True