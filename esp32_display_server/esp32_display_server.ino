// Main entry point
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

// Function declarations
void onDisplayData(uint16_t* buffer, const char* screenId);
void onConnectionChange(bool connected);
void showDisconnectedScreen();
void handleButtonPress();
void handleLongPress();

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== ESP32 Display System - Refactored ===");
  
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
      // Display off, minimal power
      // Button press will wake up
      if (input.wasShortPress() || input.wasLongPress()) {
        Serial.println("Waking from IDLE");
        stateManager.setState(STATE_DISCONNECTED);
        showDisconnectedScreen();
      }
      break;
      
    case STATE_DISCONNECTED:
      // Update network to listen for clients
      network.update();
      
      // Handle button (no action in disconnected state)
      if (input.wasShortPress()) {
        Serial.println("Button pressed in DISCONNECTED - no action");
      }
      
      if (input.wasLongPress()) {
        Serial.println("Long press in DISCONNECTED - going to IDLE");
        stateManager.setState(STATE_IDLE);
        display.fillScreen(COLOR_BLACK);
        display.update();
      }
      break;
      
    case STATE_CONNECTED:
      // Update network
      network.update();
      
      // Check for timeout
      if (!network.hasClient()) {
        Serial.println("Client disconnected - going to DISCONNECTED");
        stateManager.setState(STATE_DISCONNECTED);
        showDisconnectedScreen();
        break;
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
      break;
  }
  
  delay(10);
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
  
  if (stateManager.getState() != STATE_CONNECTED) {
    stateManager.setState(STATE_CONNECTED);
  }
}

void onConnectionChange(bool connected) {
  Serial.print("Connection changed: ");
  Serial.println(connected ? "CONNECTED" : "DISCONNECTED");
  
  if (connected) {
    stateManager.setState(STATE_CONNECTED);
  } else {
    stateManager.setState(STATE_DISCONNECTED);
    showDisconnectedScreen();
  }
}

void showDisconnectedScreen() {
  display.fillScreen(COLOR_BLACK);
  
  // Title
  display.drawText(10, 20, "Desconectado", COLOR_RED, COLOR_BLACK, 1);
  
  // Message
  display.drawText(10, 40, "Esperando", COLOR_WHITE, COLOR_BLACK, 1);
  display.drawText(10, 50, "cliente...", COLOR_WHITE, COLOR_BLACK, 1);
  
  // IP Address
  display.drawText(10, 70, "IP:", COLOR_CYAN, COLOR_BLACK, 1);
  String ip = network.getLocalIP();
  display.drawText(10, 80, ip.c_str(), COLOR_CYAN, COLOR_BLACK, 1);
  
  display.update();
}

void handleButtonPress() {
  // Short press: request next screen
  String lastScreen = stateManager.getLastScreen();
  network.sendCommand("REQUEST_NEXT_SCREEN", lastScreen.c_str());
  Serial.print("Requested next screen after: ");
  Serial.println(lastScreen);
}

void handleLongPress() {
  // Long press: request stop and go to idle
  Serial.println("Long press detected - requesting stop");
  network.sendCommand("REQUEST_STOP_SENDING");
  delay(100);  // Give time for message to send
  
  network.disconnect();
  stateManager.setState(STATE_IDLE);
  
  display.fillScreen(COLOR_BLACK);
  display.update();
}