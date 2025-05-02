import time
from periphery import GPIO
import spidev
import numpy as np
from PIL import Image

class ILI9163:
    def __init__(self, spi_bus=0, spi_device=0, dc_pin=25, rst_pin=24, cs_pin=5, width=128, height=128):
        self.width = width
        self.height = height
        self.dc = GPIO("/dev/gpiochip0", dc_pin, "out")
        self.rst = GPIO("/dev/gpiochip0", rst_pin, "out")
        self.cs = GPIO("/dev/gpiochip0", cs_pin, "out")
        self._setup_spi(spi_bus, spi_device)
        self.front_buffer = np.zeros((height, width), dtype=np.uint16)
        self.back_buffer = np.zeros_like(self.front_buffer)
        self._display_ready = False
        self._init_display()
        time.sleep(0.5)
        self._display_ready = True
        self.clear()

    def swap_buffers(self):
        np.copyto(self.front_buffer, self.back_buffer)

    def _setup_spi(self, bus, device):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 32_000_000
        self.spi.mode = 0b11
        self.spi.bits_per_word = 8
        self.spi.lsbfirst = False

    def _write(self, data, is_command=True):
        self.cs.write(False)
        self.dc.write(not is_command)
        # self.spi.transfer(data)
        self.spi.xfer2(data)
        self.cs.write(True)

    def _hardware_reset(self):
        self.rst.write(False)
        time.sleep(0.25)
        self.rst.write(True)
        time.sleep(0.3)

    def _init_display(self):
        self._hardware_reset()
        init_sequence = [
            (0x01, None, 200),            # Soft reset
            (0x11, None, 150),            # Sleep out
            (0x3A, [0x05], 10),           # Interface Pixel Format: 16bpp RGB565

            # MADCTL (0x36) Options:
            # 0x00: MY = 0, MX = 0, MV = 0 & BGR = 0.
            # 0x40: MY = 0, MX = 1, MV = 0 & BGR = 0.
            # 0x80: MY = 1, MX = 0, MV = 0 & BGR = 0.
            # 0xC0: MY = 1, MX = 1, MV = 0 & BGR = 0.
            # 0x08: MY = 0, MX = 0, MV = 0 & BGR = 1.
            # 0x48: MY = 0, MX = 1, MV = 0 & BGR = 1.
            # 0x88: MY = 1, MX = 0, MV = 0 & BGR = 1.
            # 0xC8: MY = 1, MX = 1, MV = 0 & BGR = 1.

            (0x36, [0xC8], 10),           # MADCTL: MY=1, MX=1, MV=0 → 180° & BGR
            (0xB1, [0x01, 0x2C], 10),     # Frame Rate Control
            (0xB4, [0x07], 10),           # Display Inversion Control
            (0xC0, [0x0A, 0x02], 10),     # Power Control 1
            (0xC1, [0x02], 10),           # Power Control 2
            (0xC5, [0x50, 0x5B], 10),     # VCOM Control
            (0xC7, [0x27], 10),           # VCOM Offset
            (0xE2, [0x1D, 0x0A, 0x09], 10), # Gamma Bias: Optimized for 16bpp
            # (0xE0, [                      # Positive Gamma Correction
            #     0x3F, 0x35, 0x1E, 0x1E, 0x0F,
            #     0x0C, 0x2E, 0x50, 0x47, 0x0A,
            #     0x12, 0x0C, 0x2C, 0x34, 0x0F
            # ], 10),
            # (0xE1, [                      # Negative Gamma Correction
            #     0x00, 0x27, 0x27, 0x02, 0x0D,
            #     0x09, 0x31, 0x52, 0x47, 0x09,
            #     0x14, 0x0D, 0x32, 0x36, 0x0F
            # ], 10),
            (0x2A, [0x00,0x00,0x00,0x7F], 10), # Column address 0–127
            (0x2B, [0x00,0x00,0x00,0x7F], 10), # Page address 0–127
            (0x20, None, 10),             # Display Inversion Off
            # (0x21, None, 10),           # Display Inversion On
            (0x29, None, 150)             # Display On
        ]

        for cmd, args, delay in init_sequence:
            self.cs.write(False)
            self.dc.write(False)
            self.spi.xfer2([cmd])
            if args:
                self.dc.write(True)
                self.spi.xfer2(args)
            self.cs.write(True)
            time.sleep(delay/1000)

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        x1 = x1 if x1 else self.width - 1
        y1 = y1 if y1 else self.height - 1
        self._write([0x2A] + self._pack_coords(x0, x1), True)
        self._write([0x2B] + self._pack_coords(y0, y1), True)
        self._write([0x2C], True)

    def _pack_coords(self, start, end):
        return [start >> 8, start & 0xFF, end >> 8, end & 0xFF]

    def clear(self, color=0x0000):
        self.back_buffer.fill(color)
        self.update()

    def update(self):
        if not self._display_ready:
            return
        self.swap_buffers()
        self.set_window()
        data = self.front_buffer.byteswap().tobytes()
        try:
            self._write(data, False)
        except Exception as e:
            chunk_size = 4096
            for i in range(0, len(data), chunk_size):
                self._write(data[i:i+chunk_size], False)

        # if not self._display_ready:
        #     return
        # self.swap_buffers()
        # self.cs.write(False)
        # self.dc.write(False)
        # self.spi.xfer2([0x2A] + self._pack_coords(0, self.width-1))
        # self.spi.xfer2([0x2B] + self._pack_coords(0, self.height-1))
        # self.spi.xfer2([0x2C])       # RAMWR
        # self.dc.write(True)
        # data = self.front_buffer.byteswap().tobytes()
        # try:
        #     self.spi.xfer2(data)
        # finally:
        #     self.cs.write(True)        

    def rgb_to_565(self, r, g, b):
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def display(self, image: Image.Image):
        img = image.convert('RGB').resize((self.width, self.height))
        arr = np.array(img, dtype=np.uint16)
        r = (arr[:, :, 0] & 0xF8) << 8
        g = (arr[:, :, 1] & 0xFC) << 3
        b = (arr[:, :, 2] & 0xF8) >> 3
        rgb565 = r | g | b
        np.copyto(self.back_buffer, rgb565)
        self.update()

    def __del__(self):
        try:
            self.spi.close()
        except Exception:
            pass
        try:
            self.dc.close()
            self.rst.close()
        except Exception:
            pass