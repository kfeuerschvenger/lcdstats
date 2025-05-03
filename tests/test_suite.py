import time
import sys
from pathlib import Path
from PIL import Image
from lcdstats.ILI9163 import ILI9163

disp = ILI9163()

def grid_test():
    disp.clear(0x0000) # Black background
    disp.draw_rectangle(0, 0, 1, 127, 0xFFFF) # Vertical left white line
    disp.draw_rectangle(0, 0, 20, 20, disp.rgb_to_565(127, 127, 127)) # Gray square on top left corner
    disp.draw_rectangle(0, 63, 127, 1, 0xF800) # Horizontal red line on middle
    disp.update()
    time.sleep(5)

def image_test():
    current_dir = Path(__file__).parent
    image_path = current_dir / "resources" / "test.bmp"
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    img = Image.open(image_path).resize((128, 128))
    disp.display(img)
    time.sleep(5)

def colors():
    color_list = [
        ("Red", (255, 0, 0)),
        ("Green", (0, 255, 0)),
        ("Blue", (0, 0, 255)),
        ("Yellow", (255, 255, 0)),
        ("Cyan", (0, 255, 255)),
        ("Magenta", (255, 0, 255)),
        ("White", (255, 255, 255)),
        ("Black", (0, 0, 0)),
    ]
    for name, (r, g, b) in color_list:
        print(f"Showing {name}")
        disp.clear(disp.rgb_to_565(r, g, b))
        time.sleep(1)

test_map = {
    "grid": grid_test,
    "image": image_test,
    "colors": colors,
}

def run_all_tests():
    for name, test in test_map.items():
        print(f"\n--- Running {name} test ---")
        test()

def show_menu():
    print("\nSelect a test to run:")
    for i, name in enumerate(test_map, 1):
        print(f"{i}. {name}")
    print(f"{len(test_map)+1}. all (run all tests)")
    choice = input("Enter the number of the test: ").strip()

    try:
        index = int(choice)
        if 1 <= index <= len(test_map):
            name = list(test_map.keys())[index - 1]
            test_map[name]()
        elif index == len(test_map) + 1:
            run_all_tests()
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == "all":
            run_all_tests()
        elif arg in test_map:
            test_map[arg]()
        else:
            print(f"Unknown test '{arg}'. Available tests: {', '.join(test_map)} or 'all'")
    else:
        show_menu()