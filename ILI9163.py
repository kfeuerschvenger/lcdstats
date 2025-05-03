import time
from periphery import GPIO
import spidev
import numpy as np
from PIL import Image

# GPIO chip path
GPIO_CHIP_PATH = "/dev/gpiochip0"

# Default display dimensions
DEFAULT_WIDTH = 128
DEFAULT_HEIGHT = 128

# Common color definitions (RGB565)
COLOR_BLACK = 0x0000

# SPI configuration
SPI_SPEED_HZ = 32_000_000
SPI_MODE = 0b11

# Fallback chunk size for SPI transfer
CHUNK_SIZE = 4096  

# Display command constants
CMD_SWRESET  = 0x01
CMD_SLPOUT   = 0x11
CMD_PIXFMT   = 0x3A
CMD_MADCTL   = 0x36
CMD_FRMCTR1  = 0xB1
CMD_INVCTR   = 0xB4
CMD_PWCTR1   = 0xC0
CMD_PWCTR2   = 0xC1
CMD_VMCTR1   = 0xC5
CMD_VMOFCTR  = 0xC7
CMD_GAMMASET = 0x26
CMD_GMCTRP1  = 0xE0
CMD_GMCTRN1  = 0xE1
CMD_GCV      = 0xE2
CMD_CASET    = 0x2A
CMD_PASET    = 0x2B
CMD_RAMWR    = 0x2C
CMD_INVOFF   = 0x20
CMD_DISPON   = 0x29

# MADCTL values for each rotation (including BGR bit)
ROTATION_MADCTL = {
    0:   0x08,  # BGR
    90:  0xA8,  # MX | MV | BGR
    180: 0xC8,  # MY | MX | BGR
    270: 0x68   # MY | MV | BGR
}

class ILI9163:
    def __init__(self, spi_bus=0, spi_device=0, dc_pin=25, rst_pin=24, cs_pin=5,
                 width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, rotation=180):
        self.width = width
        self.height = height
        self.rotation = rotation % 360
        self.dc = GPIO(GPIO_CHIP_PATH, dc_pin, "out")
        self.rst = GPIO(GPIO_CHIP_PATH, rst_pin, "out")
        self.cs = GPIO(GPIO_CHIP_PATH, cs_pin, "out")
        self._setup_spi(spi_bus, spi_device)
        self.front_buffer = np.zeros((height, width), dtype=np.uint16)
        self.back_buffer = np.zeros_like(self.front_buffer)
        self._display_ready = False
        self._init_display()
        time.sleep(0.5)
        self._display_ready = True
        self.clear()

    def _setup_spi(self, bus, device):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = SPI_SPEED_HZ
        self.spi.mode = SPI_MODE
        self.spi.bits_per_word = 8
        self.spi.lsbfirst = False

    def _hardware_reset(self):
        self.rst.write(False)
        time.sleep(0.25)
        self.rst.write(True)
        time.sleep(0.3)

    def _write(self, data, is_command=True):
        self.cs.write(False)
        self.dc.write(not is_command)
        self.spi.xfer2(data)
        self.cs.write(True)

    def _init_display(self):
        self._hardware_reset()
        madctl = ROTATION_MADCTL.get(self.rotation, ROTATION_MADCTL[0])

        init_sequence = [
            (CMD_SWRESET, None, 200),
            (CMD_SLPOUT, None, 150),
            (CMD_PIXFMT, [0x05], 10),        # 16 bits per pixel
            (CMD_MADCTL, [madctl], 10),      # Rotation + BGR
            (CMD_FRMCTR1, [0x01, 0x2C], 10),
            (CMD_INVCTR, [0x07], 10),
            (CMD_PWCTR1, [0x0A, 0x02], 10),
            (CMD_PWCTR2, [0x02], 10),
            (CMD_VMCTR1, [0x50, 0x5B], 10),
            (CMD_VMOFCTR, [0x27], 10),
            (CMD_GCV, [0x1D, 0x0A, 0x09], 10),
            (CMD_CASET, [0x00, 0x00, 0x00, 0x7F], 10),
            (CMD_PASET, [0x00, 0x00, 0x00, 0x7F], 10),
            (CMD_INVOFF, None, 10),
            (CMD_DISPON, None, 150)
        ]

        for cmd, args, delay in init_sequence:
            self._write([cmd], is_command=True)
            if args:
                self._write(args, is_command=False)
            time.sleep(delay / 1000)

    def _pack_coords(self, start, end):
        return [start >> 8, start & 0xFF, end >> 8, end & 0xFF]

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        x1 = x1 if x1 is not None else self.width - 1
        y1 = y1 if y1 is not None else self.height - 1
        self._write([CMD_CASET] + self._pack_coords(x0, x1), True)
        self._write([CMD_PASET] + self._pack_coords(y0, y1), True)
        self._write([CMD_RAMWR], True)

    def clear(self, color=COLOR_BLACK):
        self.back_buffer.fill(color)
        self.update()

    def update(self):
        if not self._display_ready:
            return
        self.swap_buffers()
        self.set_window()
        data = self.front_buffer.byteswap().tobytes()
        try:
            self._write(data, is_command=False)
        except Exception:
            # Fallback: send data in smaller chunks
            for i in range(0, len(data), CHUNK_SIZE):
                self._write(data[i:i+CHUNK_SIZE], is_command=False)

    def display(self, image: Image.Image):
        img = image.convert('RGB').resize((self.width, self.height))
        if self.rotation:
            img = img.rotate(self.rotation, expand=False)

        arr = np.array(img, dtype=np.uint16)
        r = (arr[:, :, 0] & 0xF8) << 8
        g = (arr[:, :, 1] & 0xFC) << 3
        b = (arr[:, :, 2] & 0xF8) >> 3
        rgb565 = r | g | b
        np.copyto(self.back_buffer, rgb565)
        self.update()

    def rgb_to_565(self, r, g, b):
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def swap_buffers(self):
        np.copyto(self.front_buffer, self.back_buffer)

    def __del__(self):
        try:
            self.spi.close()
        except Exception:
            pass
        try:
            self.dc.close()
            self.rst.close()
            self.cs.close()
        except Exception:
            pass