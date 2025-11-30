// Network and WiFi management
// ============================================================================

#ifndef NETWORK_H
#define NETWORK_H

#include <Arduino.h>
#include <ArduinoJson.h>
#include "config.h"

class WiFiServer;
class WiFiClient;
class ILI9163Display;

class NetworkManager {
private:
  WiFiServer* server;
  WiFiClient* client;
  String localIP;
  bool handshakeSent;
  String lastScreenId;

public:
  NetworkManager();
  ~NetworkManager();
  
  void begin();
  void update();
  void disconnect();
  
  bool hasClient() const;
  String getLocalIP() const { return localIP; }
  
  void sendResponse(const char* status, int code, const char* message, const char* lastScreen = nullptr);
  void sendHandshake();
  void sendCommand(const char* command, const char* extra = nullptr);
  
  // Callback for received display data
  void (*onDisplayData)(uint16_t* buffer, const char* screenId);
  void (*onConnectionChange)(bool connected);

private:
  void setupWiFi();
  void handleClient();
  bool readJsonHeader(DynamicJsonDocument& doc);
  bool readBinaryPayload(uint8_t* buffer, uint32_t length);
};

#endif