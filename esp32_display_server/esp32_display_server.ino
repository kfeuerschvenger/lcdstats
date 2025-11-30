// Main entry point - Improved stability
// ============================================================================

#include "config.h"
#include "display.h"
#include "input.h"
#include "network.h"
#include "state_manager.h"
#include "progress.h"

// Global instances
ILI9163Display display;
NetworkManager network;
InputHandler input;
StateManager stateManager;
ProgressIndicator progressIndicator;

// Debouncing and state protection
unsigned long lastStateChange = 0;
const unsigned long STATE_CHANGE_DEBOUNCE = 500;  // 500ms debounce for state changes
bool transitionInProgress = false;

// Function declarations
void onDisplayData(uint16_t* buffer, const char* screenId);
void onConnectionChange(bool connected);
void showDisconnectedScreen();
void handleButtonPress();
void handleLongPress();
bool canChangeState();

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=== ESP32 Display System ===");

  // Initialize hardware
  display.begin();
  input.begin();

  // Initialize state manager
  stateManager.begin();

  // Initialize network
  network.begin();
  network.onDisplayData = onDisplayData;
  network.onConnectionChange = onConnectionChange;

  // Show initial disconnected screen
  showDisconnectedScreen();

  Serial.println("System ready - State: DISCONNECTED");
  Serial.print("Free heap: ");
  Serial.println(ESP.getFreeHeap());
}

void loop() {
  static unsigned long lastUpdate = 0;
  unsigned long currentTime = millis();
  float deltaTime = (currentTime - lastUpdate) / 1000.0f;
  lastUpdate = currentTime;

  // Update input
  input.update();

  // Update state manager
  stateManager.update();

  // Handle state-specific logic
  DeviceState state = stateManager.getState();

  switch (state) {
    case STATE_IDLE:
      handleIdleState();
      break;

    case STATE_DISCONNECTED:
      handleDisconnectedState();
      break;

    case STATE_CONNECTED:
      handleConnectedState();
      break;
  }

  // Small delay to prevent watchdog triggers
  delay(10);
}

void handleIdleState() {
  // Display off, minimal power
  // Button press will wake up
  if (input.wasShortPress() || input.wasLongPress()) {
    if (canChangeState()) {
      Serial.println("Waking from IDLE");
      stateManager.setState(STATE_DISCONNECTED);
      showDisconnectedScreen();
      lastStateChange = millis();
    }
  }
}

void handleDisconnectedState() {
  // Update network to listen for clients
  network.update();

  // Handle short press (no action in disconnected state)
  if (input.wasShortPress()) {
    Serial.println("Button pressed in DISCONNECTED - no action");
  }

  // Handle long press (go to idle)
  if (input.wasLongPress()) {
    if (canChangeState()) {
      Serial.println("Long press in DISCONNECTED - going to IDLE");
      stateManager.setState(STATE_IDLE);
      display.fillScreen(COLOR_BLACK);
      display.update();
      lastStateChange = millis();
    }
  }
}

void handleConnectedState() {
  // Update network
  network.update();

  // Check for connection loss (client disconnected)
  if (!network.hasClient()) {
    // Add debounce to prevent rapid state changes
    if (canChangeState()) {
      Serial.println("Client disconnected - going to DISCONNECTED");
      stateManager.setState(STATE_DISCONNECTED);
      showDisconnectedScreen();
      lastStateChange = millis();
    }
    return;
  }

  // Check for activity timeout
  if (stateManager.shouldTransitionToIdle()) {
    if (canChangeState()) {
      Serial.println("Activity timeout - going to DISCONNECTED");
      stateManager.setState(STATE_DISCONNECTED);
      showDisconnectedScreen();
      lastStateChange = millis();
    }
    return;
  }

  // Handle button presses
  if (input.wasShortPress()) {
    handleButtonPress();
  }

  if (input.wasLongPress()) {
    handleLongPress();
  }

  // Draw progress indicator if button is pressed
  if (input.isButtonPressed()) {
    progressIndicator.update(input.getCurrentPressDuration());
    progressIndicator.draw(display);
    display.update();
  }
}

bool canChangeState() {
  // Prevent state changes if one is already in progress
  if (transitionInProgress) {
    return false;
  }

  // Debounce state changes
  unsigned long timeSinceLastChange = millis() - lastStateChange;
  if (timeSinceLastChange < STATE_CHANGE_DEBOUNCE) {
    Serial.print("State change debounced (");
    Serial.print(timeSinceLastChange);
    Serial.println("ms since last change)");
    return false;
  }

  return true;
}

void onDisplayData(uint16_t* buffer, const char* screenId) {
  Serial.print("Received display data for screen: ");
  Serial.println(screenId);

  // Copy buffer to display
  uint16_t* displayBuffer = display.getBuffer();
  memcpy(displayBuffer, buffer, EXPECTED_PAYLOAD_SIZE);

  // Update display
  display.update();

  // Update state
  stateManager.setLastScreen(String(screenId));
  stateManager.markActivity();

  // Transition to CONNECTED if not already
  if (stateManager.getState() != STATE_CONNECTED && canChangeState()) {
    transitionInProgress = true;
    stateManager.setState(STATE_CONNECTED);
    lastStateChange = millis();
    transitionInProgress = false;
  }
}

void onConnectionChange(bool connected) {
  Serial.print("Connection changed: ");
  Serial.println(connected ? "CONNECTED" : "DISCONNECTED");

  // Only change state if we're not in the middle of another transition
  if (!canChangeState()) {
    Serial.println("Skipping state change (debounce)");
    return;
  }

  transitionInProgress = true;

  if (connected) {
    // Don't immediately transition to CONNECTED
    // Wait for actual data (handled in onDisplayData)
    Serial.println("Client connected, waiting for data...");
  } else {
    // Client disconnected, go to DISCONNECTED state
    if (stateManager.getState() == STATE_CONNECTED) {
      stateManager.setState(STATE_DISCONNECTED);
      showDisconnectedScreen();
      lastStateChange = millis();
    }
  }

  transitionInProgress = false;
}

void showDisconnectedScreen() {
  display.fillScreen(COLOR_BLACK);

  // Title
  display.drawText(10, 20, "Disconnected", COLOR_RED, COLOR_BLACK, 1);

  // Message
  display.drawText(10, 40, "Waiting for", COLOR_WHITE, COLOR_BLACK, 1);
  display.drawText(10, 50, "client...", COLOR_WHITE, COLOR_BLACK, 1);

  // IP Address
  display.drawText(10, 70, "IP:", COLOR_CYAN, COLOR_BLACK, 1);
  String ip = network.getLocalIP();
  display.drawText(10, 80, ip.c_str(), COLOR_CYAN, COLOR_BLACK, 1);

  // Uptime info
  unsigned long uptimeSeconds = millis() / 1000;
  unsigned long uptimeMinutes = uptimeSeconds / 60;
  unsigned long uptimeHours = uptimeMinutes / 60;

  char uptimeStr[32];
  if (uptimeHours > 0) {
    snprintf(uptimeStr, sizeof(uptimeStr), "Up: %luh %lum", uptimeHours, uptimeMinutes % 60);
  } else {
    snprintf(uptimeStr, sizeof(uptimeStr), "Up: %lum", uptimeMinutes);
  }
  display.drawText(10, 100, uptimeStr, COLOR_WHITE, COLOR_BLACK, 1);

  display.update();
}

void handleButtonPress() {
  // Short press: request next screen
  String lastScreen = stateManager.getLastScreen();
  network.sendCommand("REQUEST_NEXT_SCREEN", lastScreen.c_str());
  Serial.print("Requested next screen after: ");
  Serial.println(lastScreen);

  // Mark activity to prevent timeout
  stateManager.markActivity();
}

void handleLongPress() {
  // Long press: request stop and go to idle
  if (!canChangeState()) {
    Serial.println("Long press ignored (debounce)");
    return;
  }

  Serial.println("Long press detected - requesting stop");
  network.sendCommand("REQUEST_STOP_SENDING");
  delay(100);  // Give time for message to send

  transitionInProgress = true;
  network.disconnect();
  stateManager.setState(STATE_IDLE);
  lastStateChange = millis();

  display.fillScreen(COLOR_BLACK);
  display.update();

  transitionInProgress = false;
}