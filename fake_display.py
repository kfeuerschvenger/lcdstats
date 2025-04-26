import tkinter as tk
from PIL import ImageTk, Image

class FakeDisplay:
    def __init__(self, width, height, root):
        self.width = width
        self.height = height
        self.root = root
        self.root.title("Fake LCD Display")
        self.canvas = tk.Canvas(self.root, width=width*2, height=height*2, bg="#FFFFFF", highlightthickness=0)
        self.canvas.pack()
        self.tk_image = None

    def display(self, image):
        self.tk_image = ImageTk.PhotoImage(image.convert("RGB"))
        self.canvas.create_image(self.width/2, self.height/2, anchor=tk.NW, image=self.tk_image)

    def clear(self):
        self.display(Image.new("RGB", (self.width, self.height), (0, 0, 0)))

    def update(self):
        self.root.update_idletasks()
        self.root.update()

    def close(self):
        self.root.destroy()