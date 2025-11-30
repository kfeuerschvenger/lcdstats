// Configuration constants
// ============================================================================

#ifndef CONFIG_H
#define CONFIG_H

// Display settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 128

// Pin configuration for ESP32-C3
#define TFT_CS   7
#define TFT_DC   10
#define TFT_RST  8
#define TFT_MOSI 6
#define TFT_SCLK 4

// Button pin
#define BUTTON_PIN 2

// Display offsets (calibrated for your screen)
#define COLSTART 2
#define ROWSTART 3

// SPI configuration
#define SPI_FREQUENCY 30000000
#define SPI_MODE SPI_MODE3

// Network settings
#define WIFI_SSID "YourNetworkName"
#define WIFI_PASSWORD "YourPassword"
#define SERVER_PORT 8080

// Static IP configuration
#define STATIC_IP_ENABLED true
#define STATIC_IP_0 192
#define STATIC_IP_1 168
#define STATIC_IP_2 0
#define STATIC_IP_3 199
#define GATEWAY_IP_0 192
#define GATEWAY_IP_1 168
#define GATEWAY_IP_2 0
#define GATEWAY_IP_3 1
#define SUBNET_0 255
#define SUBNET_1 255
#define SUBNET_2 255
#define SUBNET_3 0
#define PRIMARY_DNS_0 192
#define PRIMARY_DNS_1 168
#define PRIMARY_DNS_2 0
#define PRIMARY_DNS_3 1
#define SECONDARY_DNS_0 8
#define SECONDARY_DNS_1 8
#define SECONDARY_DNS_2 8
#define SECONDARY_DNS_3 8

// Timing constants
#define LONG_PRESS_THRESHOLD 3000      // 3 seconds
#define CONNECTION_TIMEOUT 30000        // 30 seconds without data = disconnected
#define DISCONNECTED_TIMEOUT 180000     // 3 minutes in disconnected = idle

// Protocol constants
#define EXPECTED_PAYLOAD_SIZE (SCREEN_WIDTH * SCREEN_HEIGHT * 2)

// Response codes
#define CODE_OK 0
#define CODE_BAD_FORMAT 1
#define CODE_AUTH_FAILED 2
#define CODE_FRAGMENT_MISSING 3
#define CODE_INTERNAL_ERROR 4

// Color definitions (RGB565)
#define COLOR_BLACK   0x0000
#define COLOR_WHITE   0xFFFF
#define COLOR_RED     0xF800
#define COLOR_GREEN   0x07E0
#define COLOR_BLUE    0x001F
#define COLOR_YELLOW  0xFFE0
#define COLOR_CYAN    0x07FF
#define COLOR_MAGENTA 0xF81F

#endif