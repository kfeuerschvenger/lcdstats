// State manager implementation
// ============================================================================

#include "state_manager.h"

StateManager::StateManager() {
  currentState = STATE_DISCONNECTED;
  stateStartTime = 0;
  lastActivityTime = 0;
  lastScreenId = "";
}

void StateManager::begin() {
  setState(STATE_DISCONNECTED);
}

void StateManager::update() {
  unsigned long now = millis();
  
  // Check transition from DISCONNECTED to IDLE
  if (currentState == STATE_DISCONNECTED) {
    if (now - stateStartTime >= DISCONNECTED_TIMEOUT) {
      setState(STATE_IDLE);
    }
  }
}

void StateManager::setState(DeviceState newState) {
  if (currentState != newState) {
    currentState = newState;
    stateStartTime = millis();
    lastActivityTime = millis();
    
    Serial.print("State changed to: ");
    switch(newState) {
      case STATE_IDLE: Serial.println("IDLE"); break;
      case STATE_DISCONNECTED: Serial.println("DISCONNECTED"); break;
      case STATE_CONNECTED: Serial.println("CONNECTED"); break;
    }
  }
}

void StateManager::markActivity() {
  lastActivityTime = millis();
}

bool StateManager::shouldTransitionToIdle() const {
  if (currentState != STATE_CONNECTED) return false;
  return (millis() - lastActivityTime) >= CONNECTION_TIMEOUT;
}