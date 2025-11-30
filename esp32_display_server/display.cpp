// Display driver implementation
// ============================================================================

#include "display.h"

// Complete 5x7 font for ASCII 32-126
const uint8_t font5x7[] PROGMEM = {
  0x00, 0x00, 0x00, 0x00, 0x00, // 32 (space)
  0x00, 0x00, 0x5F, 0x00, 0x00, // 33 !
  0x00, 0x07, 0x00, 0x07, 0x00, // 34 "
  0x14, 0x7F, 0x14, 0x7F, 0x14, // 35 #
  0x24, 0x2A, 0x7F, 0x2A, 0x12, // 36 $
  0x23, 0x13, 0x08, 0x64, 0x62, // 37 %
  0x36, 0x49, 0x55, 0x22, 0x50, // 38 &
  0x00, 0x05, 0x03, 0x00, 0x00, // 39 '
  0x00, 0x1C, 0x22, 0x41, 0x00, // 40 (
  0x00, 0x41, 0x22, 0x1C, 0x00, // 41 )
  0x14, 0x08, 0x3E, 0x08, 0x14, // 42 *
  0x08, 0x08, 0x3E, 0x08, 0x08, // 43 +
  0x00, 0x50, 0x30, 0x00, 0x00, // 44 ,
  0x08, 0x08, 0x08, 0x08, 0x08, // 45 -
  0x00, 0x60, 0x60, 0x00, 0x00, // 46 .
  0x20, 0x10, 0x08, 0x04, 0x02, // 47 /
  0x3E, 0x51, 0x49, 0x45, 0x3E, // 48 0
  0x00, 0x42, 0x7F, 0x40, 0x00, // 49 1
  0x42, 0x61, 0x51, 0x49, 0x46, // 50 2
  0x21, 0x41, 0x45, 0x4B, 0x31, // 51 3
  0x18, 0x14, 0x12, 0x7F, 0x10, // 52 4
  0x27, 0x45, 0x45, 0x45, 0x39, // 53 5
  0x3C, 0x4A, 0x49, 0x49, 0x30, // 54 6
  0x01, 0x71, 0x09, 0x05, 0x03, // 55 7
  0x36, 0x49, 0x49, 0x49, 0x36, // 56 8
  0x06, 0x49, 0x49, 0x29, 0x1E, // 57 9
  0x00, 0x36, 0x36, 0x00, 0x00, // 58 :
  0x00, 0x56, 0x36, 0x00, 0x00, // 59 ;
  0x08, 0x14, 0x22, 0x41, 0x00, // 60 <
  0x14, 0x14, 0x14, 0x14, 0x14, // 61 =
  0x00, 0x41, 0x22, 0x14, 0x08, // 62 >
  0x02, 0x01, 0x51, 0x09, 0x06, // 63 ?
  0x32, 0x49, 0x79, 0x41, 0x3E, // 64 @
  0x7E, 0x11, 0x11, 0x11, 0x7E, // 65 A
  0x7F, 0x49, 0x49, 0x49, 0x36, // 66 B
  0x3E, 0x41, 0x41, 0x41, 0x22, // 67 C
  0x7F, 0x41, 0x41, 0x22, 0x1C, // 68 D
  0x7F, 0x49, 0x49, 0x49, 0x41, // 69 E
  0x7F, 0x09, 0x09, 0x09, 0x01, // 70 F
  0x3E, 0x41, 0x49, 0x49, 0x7A, // 71 G
  0x7F, 0x08, 0x08, 0x08, 0x7F, // 72 H
  0x00, 0x41, 0x7F, 0x41, 0x00, // 73 I
  0x20, 0x40, 0x41, 0x3F, 0x01, // 74 J
  0x7F, 0x08, 0x14, 0x22, 0x41, // 75 K
  0x7F, 0x40, 0x40, 0x40, 0x40, // 76 L
  0x7F, 0x02, 0x0C, 0x02, 0x7F, // 77 M
  0x7F, 0x04, 0x08, 0x10, 0x7F, // 78 N
  0x3E, 0x41, 0x41, 0x41, 0x3E, // 79 O
  0x7F, 0x09, 0x09, 0x09, 0x06, // 80 P
  0x3E, 0x41, 0x51, 0x21, 0x5E, // 81 Q
  0x7F, 0x09, 0x19, 0x29, 0x46, // 82 R
  0x46, 0x49, 0x49, 0x49, 0x31, // 83 S
  0x01, 0x01, 0x7F, 0x01, 0x01, // 84 T
  0x3F, 0x40, 0x40, 0x40, 0x3F, // 85 U
  0x1F, 0x20, 0x40, 0x20, 0x1F, // 86 V
  0x3F, 0x40, 0x38, 0x40, 0x3F, // 87 W
  0x63, 0x14, 0x08, 0x14, 0x63, // 88 X
  0x07, 0x08, 0x70, 0x08, 0x07, // 89 Y
  0x61, 0x51, 0x49, 0x45, 0x43, // 90 Z
  0x00, 0x7F, 0x41, 0x41, 0x00, // 91 [
  0x02, 0x04, 0x08, 0x10, 0x20, // 92 backslash
  0x00, 0x41, 0x41, 0x7F, 0x00, // 93 ]
  0x04, 0x02, 0x01, 0x02, 0x04, // 94 ^
  0x40, 0x40, 0x40, 0x40, 0x40, // 95 _
  0x00, 0x01, 0x02, 0x04, 0x00, // 96 `
  0x20, 0x54, 0x54, 0x54, 0x78, // 97 a
  0x7F, 0x48, 0x44, 0x44, 0x38, // 98 b
  0x38, 0x44, 0x44, 0x44, 0x20, // 99 c
  0x38, 0x44, 0x44, 0x48, 0x7F, // 100 d
  0x38, 0x54, 0x54, 0x54, 0x18, // 101 e
  0x08, 0x7E, 0x09, 0x01, 0x02, // 102 f
  0x0C, 0x52, 0x52, 0x52, 0x3E, // 103 g
  0x7F, 0x08, 0x04, 0x04, 0x78, // 104 h
  0x00, 0x44, 0x7D, 0x40, 0x00, // 105 i
  0x20, 0x40, 0x44, 0x3D, 0x00, // 106 j
  0x7F, 0x10, 0x28, 0x44, 0x00, // 107 k
  0x00, 0x41, 0x7F, 0x40, 0x00, // 108 l
  0x7C, 0x04, 0x18, 0x04, 0x78, // 109 m
  0x7C, 0x08, 0x04, 0x04, 0x78, // 110 n
  0x38, 0x44, 0x44, 0x44, 0x38, // 111 o
  0x7C, 0x14, 0x14, 0x14, 0x08, // 112 p
  0x08, 0x14, 0x14, 0x18, 0x7C, // 113 q
  0x7C, 0x08, 0x04, 0x04, 0x08, // 114 r
  0x48, 0x54, 0x54, 0x54, 0x20, // 115 s
  0x04, 0x3F, 0x44, 0x40, 0x20, // 116 t
  0x3C, 0x40, 0x40, 0x20, 0x7C, // 117 u
  0x1C, 0x20, 0x40, 0x20, 0x1C, // 118 v
  0x3C, 0x40, 0x30, 0x40, 0x3C, // 119 w
  0x44, 0x28, 0x10, 0x28, 0x44, // 120 x
  0x0C, 0x50, 0x50, 0x50, 0x3C, // 121 y
  0x44, 0x64, 0x54, 0x4C, 0x44, // 122 z
  0x00, 0x08, 0x36, 0x41, 0x00, // 123 {
  0x00, 0x00, 0x7F, 0x00, 0x00, // 124 |
  0x00, 0x41, 0x36, 0x08, 0x00, // 125 }
  0x08, 0x04, 0x08, 0x10, 0x08, // 126 ~
};

ILI9163Display::ILI9163Display(uint8_t rot) {
  rotation = rot % 4;
  width = SCREEN_WIDTH;
  height = SCREEN_HEIGHT;
  spi = &SPI;
  buffer = new uint16_t[width * height];
  ready = false;
}

ILI9163Display::~ILI9163Display() {
  if (buffer) delete[] buffer;
}

void ILI9163Display::begin() {
  setupPins();
  setupSPI();
  initDisplay();
  ready = true;
  delay(500);
  clear();
}

void ILI9163Display::setupPins() {
  pinMode(TFT_CS, OUTPUT);
  pinMode(TFT_DC, OUTPUT);
  pinMode(TFT_RST, OUTPUT);
  
  digitalWrite(TFT_CS, HIGH);
  digitalWrite(TFT_DC, HIGH);
  digitalWrite(TFT_RST, HIGH);
}

void ILI9163Display::setupSPI() {
  spi->begin(TFT_SCLK, -1, TFT_MOSI, TFT_CS);
  spi->setFrequency(SPI_FREQUENCY);
  spi->setDataMode(SPI_MODE);
  spi->setBitOrder(MSBFIRST);
}

void ILI9163Display::hardwareReset() {
  digitalWrite(TFT_RST, LOW);
  delay(250);
  digitalWrite(TFT_RST, HIGH);
  delay(300);
}

void ILI9163Display::writeCommand(uint8_t cmd) {
  digitalWrite(TFT_CS, LOW);
  digitalWrite(TFT_DC, LOW);
  spi->transfer(cmd);
  digitalWrite(TFT_CS, HIGH);
}

void ILI9163Display::writeData(uint8_t data) {
  digitalWrite(TFT_CS, LOW);
  digitalWrite(TFT_DC, HIGH);
  spi->transfer(data);
  digitalWrite(TFT_CS, HIGH);
}

void ILI9163Display::writeDataBytes(const uint8_t* data, uint32_t len) {
  digitalWrite(TFT_CS, LOW);
  digitalWrite(TFT_DC, HIGH);
  spi->writeBytes(data, len);
  digitalWrite(TFT_CS, HIGH);
}

void ILI9163Display::initDisplay() {
  hardwareReset();
  uint8_t madctl = ROTATION_MADCTL[rotation];

  writeCommand(CMD_SWRESET); 
  delay(150);
  
  writeCommand(CMD_SLPOUT); 
  delay(255);
  
  writeCommand(CMD_PIXFMT);
  writeData(0x05);
  delay(10);
  
  writeCommand(CMD_MADCTL);
  writeData(madctl);
  delay(10);
  
  writeCommand(CMD_FRMCTR1);
  writeData(0x00);
  writeData(0x1B);
  delay(10);
  
  writeCommand(CMD_INVCTR);
  writeData(0x07);
  delay(10);
  
  writeCommand(CMD_PWCTR1);
  writeData(0x0A);
  writeData(0x02);
  delay(10);
  
  writeCommand(CMD_PWCTR2);
  writeData(0x02);
  delay(10);
  
  writeCommand(CMD_VMCTR1);
  writeData(0x50);
  writeData(0x5B);
  delay(10);
  
  writeCommand(CMD_VMOFCTR);
  writeData(0x40);
  writeData(0x8A);
  delay(10);
  
  writeCommand(CMD_NORON);
  delay(10);
  
  writeCommand(CMD_INVOFF);
  delay(10);
  
  writeCommand(CMD_DISPON);
  delay(150);
  
  clear();
}

void ILI9163Display::setWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
  x0 += COLSTART;
  x1 += COLSTART;
  y0 += ROWSTART;
  y1 += ROWSTART;
  
  writeCommand(CMD_CASET);
  writeData(x0 >> 8); 
  writeData(x0 & 0xFF);
  writeData(x1 >> 8); 
  writeData(x1 & 0xFF);
  
  writeCommand(CMD_PASET);
  writeData(y0 >> 8); 
  writeData(y0 & 0xFF);
  writeData(y1 >> 8); 
  writeData(y1 & 0xFF);
  
  writeCommand(CMD_RAMWR);
}

void ILI9163Display::clear(uint16_t color) {
  if (!ready) return;
  fillScreen(color);
  update();
}

void ILI9163Display::fillScreen(uint16_t color) {
  for (int i = 0; i < width * height; i++) {
    buffer[i] = color;
  }
}

void ILI9163Display::update() {
  if (!ready) return;
  
  setWindow(0, 0, width-1, height-1);
  
  uint8_t* data = (uint8_t*)buffer;
  uint32_t dataSize = width * height * 2;
  
  // Byte swap for display
  for (uint32_t i = 0; i < dataSize; i += 2) {
    uint8_t temp = data[i];
    data[i] = data[i+1];
    data[i+1] = temp;
  }
  
  writeDataBytes(data, dataSize);
}

void ILI9163Display::drawPixel(uint16_t x, uint16_t y, uint16_t color) {
  if (x < width && y < height) {
    buffer[y * width + x] = color;
  }
}

void ILI9163Display::drawRect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color) {
  for (uint16_t i = x; i < x + w && i < width; i++) {
    for (uint16_t j = y; j < y + h && j < height; j++) {
      drawPixel(i, j, color);
    }
  }
}

void ILI9163Display::drawLine(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1, uint16_t color) {
  int16_t dx = abs(x1 - x0);
  int16_t dy = abs(y1 - y0);
  int16_t sx = x0 < x1 ? 1 : -1;
  int16_t sy = y0 < y1 ? 1 : -1;
  int16_t err = dx - dy;

  while (true) {
    drawPixel(x0, y0, color);
    if (x0 == x1 && y0 == y1) break;
    
    int16_t e2 = 2 * err;
    if (e2 > -dy) {
      err -= dy;
      x0 += sx;
    }
    if (e2 < dx) {
      err += dx;
      y0 += sy;
    }
  }
}

void ILI9163Display::drawChar(uint16_t x, uint16_t y, char c, uint16_t color, uint16_t bg, uint8_t size) {
  if (c < 32 || c > 126) return;
  
  for (int8_t i = 0; i < 5; i++) {
    uint8_t line = pgm_read_byte(&font5x7[(c - 32) * 5 + i]);
    
    for (int8_t j = 0; j < 8; j++) {
      if (line & (1 << j)) {
        if (size == 1) {
          drawPixel(x + i, y + j, color);
        } else {
          for (uint8_t a = 0; a < size; a++) {
            for (uint8_t b = 0; b < size; b++) {
              drawPixel(x + i * size + a, y + j * size + b, color);
            }
          }
        }
      } else if (bg != color) {
        if (size == 1) {
          drawPixel(x + i, y + j, bg);
        } else {
          for (uint8_t a = 0; a < size; a++) {
            for (uint8_t b = 0; b < size; b++) {
              drawPixel(x + i * size + a, y + j * size + b, bg);
            }
          }
        }
      }
    }
  }
}

void ILI9163Display::drawText(uint16_t x, uint16_t y, const char* text, uint16_t color, uint16_t bg, uint8_t size) {
  uint16_t cursorX = x;
  uint16_t cursorY = y;
  
  while (*text) {
    if (*text == '\n') {
      cursorY += size * 8;
      cursorX = x;
    } else if (*text == '\r') {
      // Skip
    } else {
      drawChar(cursorX, cursorY, *text, color, bg, size);
      cursorX += size * 6;
      if (cursorX + 5 * size >= width) {
        cursorX = x;
        cursorY += size * 8;
      }
    }
    text++;
  }
}

uint16_t ILI9163Display::rgbTo565(uint8_t r, uint8_t g, uint8_t b) {
  return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}