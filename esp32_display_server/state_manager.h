// State manager for device states
// ============================================================================

#ifndef STATE_MANAGER_H
#define STATE_MANAGER_H

#include <Arduino.h>
#include "config.h"

enum DeviceState {
  STATE_IDLE,          // Display off, WiFi off
  STATE_DISCONNECTED,  // Display on showing IP, waiting for client
  STATE_CONNECTED      // Display showing client data
};

class StateManager {
private:
  DeviceState currentState;
  unsigned long stateStartTime;
  unsigned long lastActivityTime;
  String lastScreenId;

public:
  StateManager();
  
  void begin();
  void update();
  
  DeviceState getState() const { return currentState; }
  void setState(DeviceState newState);
  
  void markActivity();
  bool shouldTransitionToIdle() const;
  
  void setLastScreen(const String& screenId) { lastScreenId = screenId; }
  String getLastScreen() const { return lastScreenId; }
};

#endif