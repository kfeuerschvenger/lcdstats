// Display driver for ILI9163
// ============================================================================

#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#include <SPI.h>
#include "config.h"

// Display command constants
#define CMD_SWRESET  0x01
#define CMD_SLPOUT   0x11
#define CMD_PIXFMT   0x3A
#define CMD_MADCTL   0x36
#define CMD_FRMCTR1  0xB1
#define CMD_INVCTR   0xB4
#define CMD_PWCTR1   0xC0
#define CMD_PWCTR2   0xC1
#define CMD_VMCTR1   0xC5
#define CMD_VMOFCTR  0xC7
#define CMD_CASET    0x2A
#define CMD_PASET    0x2B
#define CMD_RAMWR    0x2C
#define CMD_INVOFF   0x20
#define CMD_DISPON   0x29
#define CMD_NORON    0x13

const uint8_t ROTATION_MADCTL[] = {
  0x08,  // 0: BGR
  0xA8,  // 90: MX | MV | BGR  
  0xC8,  // 180: MY | MX | BGR
  0x68   // 270: MY | MV | BGR
};

class ILI9163Display {
private:
  uint8_t rotation;
  uint16_t width, height;
  SPIClass* spi;
  uint16_t* buffer;
  bool ready;

public:
  ILI9163Display(uint8_t rot = 2);
  ~ILI9163Display();
  
  void begin();
  void clear(uint16_t color = COLOR_BLACK);
  void update();
  void setWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
  
  // Drawing functions
  void drawPixel(uint16_t x, uint16_t y, uint16_t color);
  void drawRect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color);
  void drawLine(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1, uint16_t color);
  void fillScreen(uint16_t color);
  
  // Text drawing (simple)
  void drawChar(uint16_t x, uint16_t y, char c, uint16_t color, uint16_t bg, uint8_t size);
  void drawText(uint16_t x, uint16_t y, const char* text, uint16_t color, uint16_t bg, uint8_t size);
  
  // Color conversion
  uint16_t rgbTo565(uint8_t r, uint8_t g, uint8_t b);
  
  // Get buffer pointer for direct access
  uint16_t* getBuffer() { return buffer; }
  uint16_t getWidth() { return width; }
  uint16_t getHeight() { return height; }
  bool isReady() { return ready; }

private:
  void setupPins();
  void setupSPI();
  void hardwareReset();
  void initDisplay();
  void writeCommand(uint8_t cmd);
  void writeData(uint8_t data);
  void writeDataBytes(const uint8_t* data, uint32_t len);
};

#endif