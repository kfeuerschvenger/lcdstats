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
      Serial.println("Timeout in DISCONNECTED state, transitioning to IDLE");
      setState(STATE_IDLE);
    }
  }

  // Check for connection timeout in CONNECTED state
  if (currentState == STATE_CONNECTED) {
    if (shouldTransitionToIdle()) {
      Serial.println("Connection timeout, transitioning to DISCONNECTED");
      setState(STATE_DISCONNECTED);
    }
  }
}

void StateManager::setState(DeviceState newState) {
  if (currentState != newState) {
    DeviceState previousState = currentState;
    currentState = newState;
    stateStartTime = millis();
    lastActivityTime = millis();

    Serial.print("State changed from ");
    printState(previousState);
    Serial.print(" to ");
    printState(newState);
    Serial.println();
  }
}

void StateManager::printState(DeviceState state) {
  switch(state) {
    case STATE_IDLE: Serial.print("IDLE"); break;
    case STATE_DISCONNECTED: Serial.print("DISCONNECTED"); break;
    case STATE_CONNECTED: Serial.print("CONNECTED"); break;
  }
}

void StateManager::markActivity() {
  lastActivityTime = millis();
}

bool StateManager::shouldTransitionToIdle() const {
  if (currentState != STATE_CONNECTED) return false;
  unsigned long elapsed = millis() - lastActivityTime;
  return elapsed >= CONNECTION_TIMEOUT;
}

unsigned long StateManager::getTimeSinceLastActivity() const {
  return millis() - lastActivityTime;
}

unsigned long StateManager::getTimeInCurrentState() const {
  return millis() - stateStartTime;
}