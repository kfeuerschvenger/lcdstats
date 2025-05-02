from lcdstats.ILI9163 import ILI9163
from PIL import Image
from pathlib import Path

disp = ILI9163()

def image_test():
    current_dir = Path(__file__).parent
    image_path = current_dir / "resources" / "test.bmp"
    img = Image.open(image_path)
    disp.display(img)

image_test()