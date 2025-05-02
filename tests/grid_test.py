from lcdstats.ILI9163 import ILI9163
import time

disp = ILI9163()

def grid_test():
    # Black background
    disp.clear(0x0000)
    
    # Vertical left white line
    disp.draw_rectangle(0, 0, 1, 127, 0xFFFF)
    
    # Gray square on top left corner
    disp.draw_rectangle(0, 0, 20, 20, disp.rgb_to_565(127, 127, 127))
    
    # Horizontal red line on middle
    disp.draw_rectangle(0, 63, 127, 1, 0xF800)
    
    disp.update()
    time.sleep(5)

grid_test()