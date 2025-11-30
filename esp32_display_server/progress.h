// Progress indicator for long press
// ============================================================================

#ifndef PROGRESS_H
#define PROGRESS_H

#include <Arduino.h>
#include "display.h"
#include "config.h"

class ProgressIndicator {
private:
  float currentProgress;
  bool visible;
  
  static const int RADIUS = 12;
  static const int THICKNESS = 3;
  static const int MARGIN = 10;

public:
  ProgressIndicator();
  
  void update(float pressDuration);
  void draw(ILI9163Display& display);

private:
  void drawArc(ILI9163Display& display, int cx, int cy, int r, float startAngle, float endAngle, uint16_t color);
  uint16_t interpolateColor(float progress);
};

#endif