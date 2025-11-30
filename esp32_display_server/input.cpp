// Button input implementation
// ============================================================================

#include "input.h"

InputHandler::InputHandler(uint8_t pin) {
  buttonPin = pin;
  isPressed = false;
  shortPressDetected = false;
  longPressDetected = false;
  longPressHandled = false;
  pressStartTime = 0;
}

void InputHandler::begin() {
  pinMode(buttonPin, INPUT_PULLUP);
}

void InputHandler::update() {
  bool currentState = digitalRead(buttonPin) == LOW; // Active low
  
  if (currentState && !isPressed) {
    // Button just pressed
    isPressed = true;
    pressStartTime = millis();
    longPressHandled = false;
  } else if (!currentState && isPressed) {
    // Button just released
    unsigned long pressDuration = millis() - pressStartTime;
    isPressed = false;
    
    if (pressDuration >= LONG_PRESS_THRESHOLD) {
      if (!longPressHandled) {
        longPressDetected = true;
      }
    } else {
      shortPressDetected = true;
    }
  } else if (isPressed && !longPressHandled) {
    // Check for long press while still pressed
    if (millis() - pressStartTime >= LONG_PRESS_THRESHOLD) {
      longPressDetected = true;
      longPressHandled = true;
    }
  }
}

bool InputHandler::wasShortPress() {
  bool result = shortPressDetected;
  shortPressDetected = false;
  return result;
}

bool InputHandler::wasLongPress() {
  bool result = longPressDetected;
  longPressDetected = false;
  return result;
}

float InputHandler::getCurrentPressDuration() {
  if (!isPressed) return 0.0f;
  return (millis() - pressStartTime) / 1000.0f;
}

bool InputHandler::isButtonPressed() {
  return isPressed;
}