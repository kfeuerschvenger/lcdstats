import tkinter as tk
from PIL import ImageTk, Image

# Constants
SCALE_FACTOR = 2  # Scale the canvas for better visibility in simulation
BACKGROUND_COLOR = "#FFFFFF"  # Background color of the canvas
CLEAR_COLOR = (0, 0, 0)  # RGB color used when clearing the screen

class FakeDisplay:
    def __init__(self, width: int, height: int, root: tk.Tk):
        self.width = width
        self.height = height
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
        
        rgb_image = image.convert("RGB")
        try:
            self.tk_image = ImageTk.PhotoImage(rgb_image, master=self.root)
            self.canvas.create_image(
                self.width // 2,
                self.height // 2,
                anchor=tk.NW,
                image=self.tk_image
            )
        except tk.TclError:
            self.closed = True

    def clear(self):
        """Clear the display by filling it with black."""
        if not self.closed:
            try:
                self.display(Image.new("RGB", (self.width, self.height), CLEAR_COLOR))
            except tk.TclError:
                self.closed = True

    def update(self):
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