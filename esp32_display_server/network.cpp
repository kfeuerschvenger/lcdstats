// network.cpp - Refactored protocol implementation
// ============================================================================

#include "network.h"
#include <WiFi.h>

NetworkManager::NetworkManager() {
  server = nullptr;
  client = nullptr;
  handshakeSent = false;
  onDisplayData = nullptr;
  onConnectionChange = nullptr;
  lastScreenId = "";
}

NetworkManager::~NetworkManager() {
  disconnect();
  if (server) {
    server->end();
    delete server;
    server = nullptr;
  }
}

void NetworkManager::setupWiFi() {
  WiFi.mode(WIFI_STA);
  
#ifdef STATIC_IP_ENABLED
  IPAddress staticIP(STATIC_IP_0, STATIC_IP_1, STATIC_IP_2, STATIC_IP_3);
  IPAddress gateway(GATEWAY_IP_0, GATEWAY_IP_1, GATEWAY_IP_2, GATEWAY_IP_3);
  IPAddress subnet(SUBNET_0, SUBNET_1, SUBNET_2, SUBNET_3);
  IPAddress primaryDNS(PRIMARY_DNS_0, PRIMARY_DNS_1, PRIMARY_DNS_2, PRIMARY_DNS_3);
  IPAddress secondaryDNS(SECONDARY_DNS_0, SECONDARY_DNS_1, SECONDARY_DNS_2, SECONDARY_DNS_3);
  
  if (!WiFi.config(staticIP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("Failed to configure static IP");
  }
#endif
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    localIP = WiFi.localIP().toString();
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(localIP);
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

void NetworkManager::begin() {
  setupWiFi();
  
  if (WiFi.status() == WL_CONNECTED) {
    server = new WiFiServer(SERVER_PORT);
    server->begin();
    Serial.println("Server started on port " + String(SERVER_PORT));
  }
}

void NetworkManager::update() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  // Check for new client
  if (!client || !client->connected()) {
    if (client) {
      bool wasConnected = handshakeSent;
      delete client;
      client = nullptr;
      handshakeSent = false;
      
      if (wasConnected && onConnectionChange) {
        onConnectionChange(false);
      }
    }
    
    WiFiClient newClient = server->available();
    if (newClient) {
      client = new WiFiClient(newClient);
      Serial.println("New client connected");
      sendHandshake();
      handshakeSent = true;
      
      if (onConnectionChange) {
        onConnectionChange(true);
      }
    }
  }
  
  // Handle client data
  if (client && client->available()) {
    handleClient();
  }
}

void NetworkManager::disconnect() {
  if (client) {
    client->stop();
    delete client;
    client = nullptr;
    handshakeSent = false;
    
    if (onConnectionChange) {
      onConnectionChange(false);
    }
  }
}

bool NetworkManager::hasClient() const {
  return client && client->connected() && handshakeSent;
}

void NetworkManager::sendHandshake() {
  DynamicJsonDocument doc(256);
  doc["status"] = "ready";
  doc["code"] = CODE_OK;
  doc["width"] = SCREEN_WIDTH;
  doc["height"] = SCREEN_HEIGHT;
  doc["format"] = "RGB565";
  doc["endianness"] = "little";
  
  String output;
  serializeJson(doc, output);
  client->println(output);
  Serial.println("Handshake sent: " + output);
}

void NetworkManager::sendResponse(const char* status, int code, const char* message, const char* lastScreen) {
  if (!client) return;
  
  DynamicJsonDocument doc(512);
  doc["status"] = status;
  doc["code"] = code;
  if (message) doc["message"] = message;
  if (lastScreen) doc["lastScreen"] = lastScreen;
  
  String output;
  serializeJson(doc, output);
  client->println(output);
  Serial.println("Response: " + output);
}

void NetworkManager::sendCommand(const char* command, const char* extra) {
  if (!client) return;
  
  DynamicJsonDocument doc(256);
  doc["command"] = command;
  if (extra) doc["last"] = extra;
  
  String output;
  serializeJson(doc, output);
  client->println(output);
  Serial.println("Command sent: " + output);
}

bool NetworkManager::readJsonHeader(DynamicJsonDocument& doc) {
  if (!client || !client->available()) return false;
  
  String line = client->readStringUntil('\n');
  line.trim();
  
  if (line.length() == 0) return false;
  
  Serial.println("Received JSON: " + line);
  
  DeserializationError error = deserializeJson(doc, line);
  if (error) {
    Serial.print("JSON parse error: ");
    Serial.println(error.c_str());
    sendResponse("error", CODE_BAD_FORMAT, "Invalid JSON");
    return false;
  }
  
  return true;
}

bool NetworkManager::readBinaryPayload(uint8_t* buffer, uint32_t length) {
  if (!client) return false;
  
  uint32_t bytesRead = 0;
  unsigned long startTime = millis();
  
  while (bytesRead < length) {
    if (millis() - startTime > 5000) {  // 5 second timeout
      Serial.println("Timeout reading payload");
      return false;
    }
    
    if (client->available()) {
      int available = client->available();
      int toRead = min(available, (int)(length - bytesRead));
      int read = client->readBytes(buffer + bytesRead, toRead);
      bytesRead += read;
    }
    
    if (!client->connected()) {
      Serial.println("Client disconnected during payload read");
      return false;
    }
    
    delay(1);
  }
  
  return bytesRead == length;
}

void NetworkManager::handleClient() {
  if (!client) return;
  
  DynamicJsonDocument doc(1024);
  if (!readJsonHeader(doc)) return;
  
  const char* command = doc["command"];
  if (!command) {
    sendResponse("error", CODE_BAD_FORMAT, "Missing command field");
    return;
  }
  
  if (strcmp(command, "DISPLAY") == 0) {
    uint32_t length = doc["length"];
    const char* screenId = doc["screen_id"];
    
    if (length != EXPECTED_PAYLOAD_SIZE) {
      sendResponse("error", CODE_BAD_FORMAT, "Invalid payload length");
      return;
    }
    
    if (!screenId) {
      sendResponse("error", CODE_BAD_FORMAT, "Missing screen_id");
      return;
    }
    
    // Send ready response
    sendResponse("ready", CODE_OK, "Waiting for payload");
    
    // Read binary payload
    uint8_t* payloadBuffer = new uint8_t[length];
    bool success = readBinaryPayload(payloadBuffer, length);
    
    if (!success) {
      delete[] payloadBuffer;
      sendResponse("error", CODE_FRAGMENT_MISSING, "Incomplete payload");
      return;
    }
    
    // Convert to RGB565 and call callback
    if (onDisplayData) {
      uint16_t* rgb565Buffer = (uint16_t*)payloadBuffer;
      onDisplayData(rgb565Buffer, screenId);
      lastScreenId = String(screenId);
    }
    
    delete[] payloadBuffer;
    sendResponse("ok", CODE_OK, "displayed", screenId);
    
  } else {
    sendResponse("error", CODE_BAD_FORMAT, "Unknown command");
  }
}