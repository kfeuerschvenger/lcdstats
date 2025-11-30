// Progress indicator implementation
// ============================================================================

#include <Arduino.h>
#include "progress.h"

#ifndef PI
#define PI 3.14159265358979323846
#endif

ProgressIndicator::ProgressIndicator() {
  currentProgress = 0;
  visible = false;
}

void ProgressIndicator::update(float pressDuration) {
  if (pressDuration > 0.2f && pressDuration < 3.0f) {
    visible = true;
    currentProgress = pressDuration / 3.0f;
  } else {
    visible = false;
    currentProgress = 0;
  }
}

void ProgressIndicator::draw(ILI9163Display& display) {
  if (!visible) return;
  
  int cx = display.getWidth() - RADIUS - MARGIN;
  int cy = display.getHeight() - RADIUS - MARGIN;
  
  // Draw background circle
  for (int r = RADIUS - THICKNESS; r <= RADIUS; r++) {
    drawArc(display, cx, cy, r, 0, 360, display.rgbTo565(30, 30, 30));
  }
  
  // Draw progress arc
  uint16_t color = interpolateColor(currentProgress);
  float endAngle = -90 + (360 * currentProgress);
  
  for (int r = RADIUS - THICKNESS; r <= RADIUS; r++) {
    drawArc(display, cx, cy, r, -90, endAngle, color);
  }
}

void ProgressIndicator::drawArc(ILI9163Display& display, int cx, int cy, int r, float startAngle, float endAngle, uint16_t color) {
  float step = 2.0f / r;
  
  for (float angle = startAngle; angle <= endAngle; angle += step) {
    float rad = angle * PI / 180.0f;
    int x = cx + (int)(r * cos(rad));
    int y = cy + (int)(r * sin(rad));
    display.drawPixel(x, y, color);
  }
}

uint16_t ProgressIndicator::interpolateColor(float progress) {
  uint8_t r = (uint8_t)(255 * progress);
  uint8_t g = (uint8_t)(255 * (1 - progress));
  return ((r & 0xF8) << 8) | ((g & 0xFC) << 3);
}