// Network and WiFi management implementation
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
  lastClientCheck = 0;
  consecutiveErrors = 0;
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
  WiFi.setAutoReconnect(true);  // Enable auto-reconnect
  
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
    Serial.print("Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

void NetworkManager::begin() {
  setupWiFi();
  
  if (WiFi.status() == WL_CONNECTED) {
    server = new WiFiServer(SERVER_PORT);
    server->begin();
    server->setNoDelay(true);  // Disable Nagle's algorithm for lower latency
    Serial.println("Server started on port " + String(SERVER_PORT));
  }
}

void NetworkManager::update() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, attempting reconnect...");
    setupWiFi();
    return;
  }
  
  unsigned long now = millis();
  
  // Periodic client health check (every 5 seconds)
  if (client && (now - lastClientCheck > 5000)) {
    lastClientCheck = now;
    
    if (!client->connected()) {
      Serial.println("Client health check failed");
      handleClientDisconnect();
      return;
    }
  }
  
  // Check for new client
  if (!client || !client->connected()) {
    if (client) {
      handleClientDisconnect();
    }
    
    WiFiClient newClient = server->available();
    if (newClient) {
      client = new WiFiClient(newClient);
      client->setNoDelay(true);  // Disable Nagle's algorithm
      
      Serial.println("New client connected");
      Serial.print("Client IP: ");
      Serial.println(client->remoteIP());
      
      sendHandshake();
      handshakeSent = true;
      consecutiveErrors = 0;
      lastClientCheck = millis();
      
      if (onConnectionChange) {
        onConnectionChange(true);
      }
    }
  }
  
  // Handle client data
  if (client && client->available()) {
    if (!handleClient()) {
      consecutiveErrors++;
      if (consecutiveErrors >= 3) {
        Serial.println("Too many consecutive errors, disconnecting client");
        handleClientDisconnect();
      }
    } else {
      consecutiveErrors = 0;
    }
  }
}

void NetworkManager::handleClientDisconnect() {
  bool wasConnected = handshakeSent;
  
  if (client) {
    client->stop();
    delete client;
    client = nullptr;
  }
  
  handshakeSent = false;
  consecutiveErrors = 0;
  
  if (wasConnected && onConnectionChange) {
    onConnectionChange(false);
  }
}

void NetworkManager::disconnect() {
  handleClientDisconnect();
}

bool NetworkManager::hasClient() const {
  return client && client->connected() && handshakeSent;
}

void NetworkManager::sendHandshake() {
  if (!client) return;
  
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
  client->flush();  // Ensure data is sent immediately
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
  client->flush();
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
  client->flush();
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
  const unsigned long PAYLOAD_TIMEOUT = 5000;  // 5 second timeout
  
  while (bytesRead < length) {
    if (millis() - startTime > PAYLOAD_TIMEOUT) {
      Serial.print("Timeout reading payload: ");
      Serial.print(bytesRead);
      Serial.print("/");
      Serial.println(length);
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

bool NetworkManager::handleClient() {
  if (!client) return false;
  
  DynamicJsonDocument doc(1024);
  if (!readJsonHeader(doc)) return false;
  
  const char* command = doc["command"];
  if (!command) {
    sendResponse("error", CODE_BAD_FORMAT, "Missing command field");
    return false;
  }
  
  if (strcmp(command, "DISPLAY") == 0) {
    uint32_t length = doc["length"];
    const char* screenId = doc["screen_id"];
    
    if (length != EXPECTED_PAYLOAD_SIZE) {
      sendResponse("error", CODE_BAD_FORMAT, "Invalid payload length");
      return false;
    }
    
    if (!screenId) {
      sendResponse("error", CODE_BAD_FORMAT, "Missing screen_id");
      return false;
    }
    
    // Send ready response
    sendResponse("ready", CODE_OK, "Waiting for payload");
    
    // Read binary payload
    uint8_t* payloadBuffer = new uint8_t[length];
    bool success = readBinaryPayload(payloadBuffer, length);
    
    if (!success) {
      delete[] payloadBuffer;
      sendResponse("error", CODE_FRAGMENT_MISSING, "Incomplete payload");
      return false;
    }
    
    // Convert to RGB565 and call callback
    if (onDisplayData) {
      uint16_t* rgb565Buffer = (uint16_t*)payloadBuffer;
      onDisplayData(rgb565Buffer, screenId);
      lastScreenId = String(screenId);
    }
    
    delete[] payloadBuffer;
    sendResponse("ok", CODE_OK, "displayed", screenId);
    return true;
    
  } else {
    sendResponse("error", CODE_BAD_FORMAT, "Unknown command");
    return false;
  }
}