from lcdstats.ILI9163 import ILI9163
import time

disp = ILI9163()

def sanity_check():
    for color_name, (r,g,b) in [('Red',(255,0,0)), ('Green',(0,255,0)), ('Blue',(0,0,255))]:
        disp.clear(disp.rgb_to_565(* (r,g,b)))
        print("Showing", color_name)
        time.sleep(2)

def all_in_one():
    # Vertical strips
    disp.draw_rectangle(0, 0, 43, 127, disp.rgb_to_565(255,0,0)) # Red
    disp.draw_rectangle(43, 0, 42, 127, disp.rgb_to_565(0,255,0)) # Green
    disp.draw_rectangle(85, 0, 43, 127, disp.rgb_to_565(0,0,255)) # Blue
    disp.update()

def colors():
    disp.clear(disp.rgb_to_565(255, 0, 0))  # Red
    time.sleep(1)
    disp.clear(disp.rgb_to_565(0, 255, 0))  # Green
    time.sleep(1)
    disp.clear(disp.rgb_to_565(0, 0, 255))  # Blue
    time.sleep(1)
    disp.clear(disp.rgb_to_565(255, 255, 0)) # Yellow
    time.sleep(1)
    disp.clear(disp.rgb_to_565(0, 255, 255)) # Cyan
    time.sleep(1)
    disp.clear(disp.rgb_to_565(255, 0, 255)) # Magenta
    time.sleep(1)
    disp.clear(disp.rgb_to_565(255, 255, 255)) # White
    time.sleep(1)
    disp.clear(disp.rgb_to_565(0, 0, 0))     # Black

# sanity_check()
# all_in_one()
colors()