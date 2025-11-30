// Button input handler
// ============================================================================

#ifndef INPUT_H
#define INPUT_H

#include <Arduino.h>
#include "config.h"

class InputHandler {
private:
  uint8_t buttonPin;
  bool isPressed;
  bool shortPressDetected;
  bool longPressDetected;
  bool longPressHandled;
  unsigned long pressStartTime;

public:
  InputHandler(uint8_t pin = BUTTON_PIN);
  
  void begin();
  void update();
  
  bool wasShortPress();
  bool wasLongPress();
  float getCurrentPressDuration();
  bool isButtonPressed();
};

#endif