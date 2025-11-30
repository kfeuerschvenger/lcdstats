# Raspberry Pi System Monitor LCD Panel

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A multi-mode system monitor for Raspberry Pi with support for:
- **Direct LCD display** (ILI9163 via SPI)
- **ESP32 WiFi display** (remote wireless screen)
- **Windows simulation** (Tkinter GUI for development)

## Motivation

I recently got a Raspberry Pi 5 to set up my own home server. I'm hosting my website on it and have some exciting future projects lined up. I wanted a way to monitor system stats from my desk, so I developed this project to display important information like public IP, local IP, CPU temperature, memory usage, disk usage, and other metrics.

The app supports three display modes:
- **Native LCD**: Direct connection to ILI9163 display on Raspberry Pi
- **ESP32 WiFi**: Wireless streaming to an ESP32-C3 with LCD display
- **Simulation**: Windows development mode with Tkinter window

## Features

- **Real-time monitoring**:
  - Public & Local IP Addresses
  - CPU Usage & Temperature
  - Memory Utilization
  - Disk Space
  - System Uptime
  - Current Time
- **Multi-screen support** with button navigation
- **Three display modes**:
  - Native SPI LCD (ILI9163)
  - WiFi streaming to ESP32
  - Desktop simulation (Windows/Tkinter)
- **Hardware acceleration** for SPI displays
- **Modular architecture**:
  - Screen Management System
  - Hardware Abstraction Layer
  - Input Handling Framework

## Display Modes

### 1. Native LCD (Raspberry Pi)
Direct SPI connection to 1.44" 128x128 ILI9163 display. Lowest latency, requires physical wiring.

### 2. ESP32 WiFi Display
Stream display data over WiFi to an ESP32-C3 with attached LCD. Benefits:
- No physical connection required
- Flexible placement
- Can be powered independently
- Same visual output as native mode

### 3. Windows Simulation
Development mode with Tkinter window showing what would appear on the LCD.

## Project Structure

```bash
lcdstats/
├── devices/
│   ├── device.py                 # Interface for display devices
│   ├── fake_display.py           # Tkinter-based simulator
│   ├── ILI9163.py                # Native SPI LCD driver
│   └── esp32_wifi_display.py     # WiFi streaming client
├── esp32_display_server/         # ESP32 firmware (Arduino)
│   ├── config.h                  # WiFi & hardware config
│   ├── display.h/cpp             # ILI9163 driver for ESP32
│   ├── input.h/cpp               # Button handler
│   ├── network.h/cpp             # WiFi protocol
│   ├── state_manager.h/cpp       # Device state machine
│   ├── progress.h/cpp            # Progress indicator UI
│   └── esp32_display_server.ino  # Main firmware
├── fonts/                        # Custom fonts
├── resources/                    # Graphics (icons, GIFs)
├── tests/                        # Validation suite
├── utils/                        # Helper classes
│   └── progress_indicator.py     # Circular progress widget
├── views/                        # UI Screen implementations
│   ├── screen.py                 # Abstract base class
│   ├── main_screen.py            # System metrics display
│   └── secondary_screen.py       # Media/animation display
├── data_gatherer.py              # System metrics collector
├── input_handler.py              # Input processor
├── screen_manager.py             # Screen state controller
├── stats.py                      # Main application
├── Dockerfile                    # Docker container config
└── docker-compose.yml            # Docker orchestration
```

## Hardware Requirements

### Native LCD Setup (Raspberry Pi)
| Component    | Specification                          |
| ------------ | -------------------------------------- |
| Raspberry Pi | Model 3B+/4/5 (Tested on Pi 5)         |
| Display      | 1.44" 128x128 SPI TFT (ILI9163 driver) |
| Button       | Momentary push button (Normally Open)  |

### ESP32 WiFi Display Setup
| Component    | Specification                          |
| ------------ | -------------------------------------- |
| Raspberry Pi | Model 3B+/4/5 (runs Python client)     |
| ESP32        | ESP32-C3 or similar                    |
| Display      | 1.44" 128x128 SPI TFT (ILI9163 driver) |
| Button       | Momentary push button (Normally Open)  |

## Software Dependencies

```bash
# requirements.txt (Raspberry Pi - Native mode)
Pillow==10.3.0      # Image processing
numpy==1.26.4       # Buffer management
periphery==2.1.1    # GPIO control
spidev==3.6         # SPI communication

# requirements-windows.txt (Development)
Pillow==10.3.0
numpy==1.26.4
tkinter==0.1.0      # GUI framework
```

## Wiring Diagrams

### Native LCD Mode (Raspberry Pi → ILI9163)

| Pin               | Physical Pin | Raspberry Pi   | Function            |
|:-----------------:|:------------:|:--------------:|:--------------------|
| VCC               | Pin 1        | 3.3V Power     | Power supply        |
| GND               | Pin 6        | Ground         | Common ground       |
| SCL               | Pin 23       | GPIO 11 (SCLK) | SPI Clock           |
| SDA               | Pin 19       | GPIO 10 (MOSI) | SPI Data            |
| RES (Reset)       | Pin 22       | GPIO 25        | Display Reset       |
| DC (Data/Command) | Pin 18       | GPIO 24        | Data/Command Select |
| CS                | Pin 29       | GPIO 5         | Chip Select         |
| LED               | Pin 17       | 3.3V Power     | Backlight Power     |
| Button Signal     | Pin 12       | GPIO 18        | Button input        |
| Button Ground     | Pin 9        | Ground         | Button return path  |

### ESP32 WiFi Mode (ESP32-C3 → ILI9163)

| Pin               | ESP32-C3 GPIO | Function            |
|:-----------------:|:-------------:|:--------------------|
| VCC	              |     3.3V      | Power supply        |
| GND	              |     GND       | Common ground       |
| CS	              |    GPIO 7     | Chip Select         |
| RST	              |    GPIO 8     | Display Reset       |
| RS	              |    GPIO 10    | Data/Command Select |
| SDI	              |    GPIO 6     | SPI Data (MOSI)     |
| CLK	              |    GPIO 4     | SPI Clock           |
| LED               |     3.3V      | Backlight Power     |
|   Button Signal   |    GPIO 2     | Button input        |
|   Button Ground   |     GND       | Button return path  |

**Note**: ESP32 button uses internal pull-up, no external resistor needed.

## Installation

### Option 1: Native Installation (Raspberry Pi)

```bash
# 1. Install system dependencies
sudo apt update && sudo apt install -y \
  python3-dev \
  libgpiod-dev \
  libjpeg-dev \
  zlib1g-dev \
  python3-spidev

# 2. Create and activate virtual environment
python -m venv stats_env
source stats_env/bin/activate

# 3. Install Python packages
pip install -r requirements.txt
```

### Option 2: Docker Installation (Recommended for Raspberry Pi)

**Important Note on Docker Mode:**

When running in Docker, the app **cannot access real system metrics** (CPU temp, memory usage, etc.) because it's isolated in a container. Docker mode is primarily useful for:
- **ESP32 WiFi display**: Stream to remote display (works perfectly)
- **Development/Testing**: Simulated data for UI testing
- **Portability**: Easy deployment without system dependencies

For **native LCD with real metrics**, use native installation (Option 1).

```bash
# Quick start with docker-compose
docker-compose up -d

# Or build and run manually
docker build -t lcdstats .
docker run -d \
  --name lcdstats \
  --network host \
  -e DISPLAY_MODE=esp32 \
  -e ESP32_HOST=192.168.0.199 \
  lcdstats
```

**Docker environment variables:**
- `DISPLAY_MODE`: `window` (default), `esp32`, or `raspberry`
- `ESP32_HOST`: IP address of ESP32 (required for `esp32` mode)

### Option 3: Windows Simulation Setup

```bash
# 1. Create virtual environment
python -m venv stats_env
stats_env\Scripts\activate

# 2. Install dependencies
pip install -r requirements-windows.txt
```

### ESP32 Firmware Installation

1. **Install Arduino IDE and ESP32 board support**:
   - Download [Arduino IDE](https://www.arduino.cc/en/software)
   - Go to Tools → Board → Board Manager
   - Search for "esp32" and install "esp32 by Espressif Systems"

2. **Install required libraries**:
   - Go to Tools → Manage Libraries (or Sketch → Include Library → Manage Libraries)
   - Search and install: **ArduinoJson** (by Benoit Blanchon)

3. **Configure WiFi** in `esp32_display_server/config.h`:
   ```cpp
   #define WIFI_SSID "YourNetworkName"
   #define WIFI_PASSWORD "YourPassword"  // Plain text password (to be improved in future releases)
   
   // Optional: Set static IP (recommended)
   #define STATIC_IP_ENABLED true
   #define STATIC_IP_0 192
   #define STATIC_IP_1 168
   #define STATIC_IP_2 0
   #define STATIC_IP_3 199  // Last octet (change as needed)
   ```

4. **Upload firmware**:
   - Connect ESP32 to your computer via USB
   - Open `esp32_display_server/esp32_display_server.ino` in Arduino IDE
   - Select board: **Tools → Board → ESP32 Arduino → ESP32C3 Dev Module**
   - Select port: **Tools → Port → (your COM port or /dev/ttyUSB0)**
   - Click **Upload** button (→)
   - Wait for "Done uploading" message

5. **Verify operation**:
   - Open **Tools → Serial Monitor** (set to 115200 baud)
   - Press the **RESET** button on your ESP32
   - You should see:
     ```
     === ESP32 Display System - Refactored ===
     Connecting to WiFi....
     WiFi Connected!
     IP Address: 192.168.0.199
     Server started on port 8080
     System ready - State: DISCONNECTED
     ```
   - The LCD should display "Desconectado" with the IP address

6. **Note the IP address** shown on the ESP32 display - you'll need it for the Python client

## Usage

### Native LCD Mode (Direct SPI)
```bash
source stats_env/bin/activate
python stats.py --display raspberry
```

### ESP32 WiFi Mode (Wireless)
```bash
# Make sure ESP32 is powered and showing its IP
source stats_env/bin/activate
python stats.py --display esp32 --esp32-host 192.168.0.199
```

### Docker Mode (ESP32 WiFi)
```bash
# Edit docker-compose.yml with your ESP32 IP, then:
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Windows Simulation Mode
```bash
stats_env\Scripts\activate
python stats.py --display window
```

### Controls

- **Short press**: Cycle through screens
- **Long press (3 seconds)**: Toggle display on/off
- **Spacebar** (simulation mode): Emulates button press

## Communication Protocol (ESP32 WiFi Mode)

The Python client and ESP32 communicate over TCP port 8080 using a JSON + binary protocol:

1. **Handshake**: ESP32 sends capabilities (width, height, format)
2. **Display Command**: Client sends JSON header + RGB565 binary payload
3. **Acknowledgment**: ESP32 confirms receipt or requests retransmission
4. **Commands**: ESP32 can request next screen or stop sending

Protocol features:
- Automatic reconnection with exponential backoff
- Fragmentation detection and retry logic
- Error codes for debugging
- Screen ID tracking for synchronization

## Run Tests

```bash
python -m lcdstats.tests.test_suite           # Interactive menu
python -m lcdstats.tests.test_suite all       # Run all tests
python -m lcdstats.tests.test_suite image     # Run specific test
```

## Troubleshooting

### ESP32 WiFi Display Issues

**Problem**: ESP32 shows "Disconnected" screen  
**Solution**:
- Check WiFi credentials in `config.h` (use plain text password, not PSK hash)
- Verify ESP32 and Raspberry Pi are on same network
- Open Serial Monitor (115200 baud) to check for WiFi errors
- Try power cycling the ESP32 (unplug and plug back in)

**Problem**: Python client cannot connect ("Connection timeout" or "No handshake")  
**Solution**:
- Verify ESP32 is showing "Desconectado" with IP address on screen
- Test connectivity from Raspberry Pi: `ping <esp32-ip>`
- Test TCP port: `nc -zv <esp32-ip> 8080` or `telnet <esp32-ip> 8080`
- Check ESP32 Serial Monitor for errors or crashes
- **Power cycle the ESP32** - unplug and reconnect (common fix!)
- Verify firewall isn't blocking port 8080
- Try re-uploading the firmware with Arduino IDE

**Problem**: Display freezes or shows artifacts  
**Solution**:
- Check SPI connections (loose wires between ESP32 and LCD)
- Reduce SPI frequency in `config.h` if needed (try 20MHz instead of 30MHz)
- Verify power supply stability (use quality USB cable, 5V 1A minimum)
- Check for loose connections on breadboard

**Problem**: ESP32 won't connect to WiFi  
**Solution**:
- Double-check SSID and password in `config.h` (case-sensitive!)
- Ensure WiFi is 2.4GHz (ESP32-C3 doesn't support 5GHz)
- Check if MAC filtering is enabled on your router
- Try disabling static IP (`STATIC_IP_ENABLED false`) to use DHCP
- Open Serial Monitor to see actual error messages

**Problem**: Docker container keeps restarting  
**Solution**:
- Check logs: `docker logs lcdstats`
- Common issues:
  - ESP32 not reachable: verify with `ping <esp32-ip>`
  - Wrong ESP32_HOST in docker-compose.yml
  - ESP32 not powered on or firmware not uploaded
- Try rebuilding: `docker-compose down && docker-compose build --no-cache && docker-compose up`

### Docker Mode Issues

**Problem**: Cannot connect to ESP32 from Docker  
**Solution**:
- Verify `network_mode: host` is set in docker-compose.yml
- Test connectivity from host: `ping <esp32-ip>` should work
- Check ESP32_HOST environment variable matches actual ESP32 IP
- Ensure ESP32 is on same network as Raspberry Pi

**Problem**: System metrics show weird/simulated data  
**Solution**:
- Verify `IS_RASPBERRY: "true"` in docker-compose.yml
- Check that privileged mode is enabled
- Verify volumes are mounted: `/sys:/sys:ro` and `/proc:/proc:ro`
- Rebuild container: `docker-compose build --no-cache`

**Problem**: "Could not find a version that satisfies the requirement periphery"  
**Solution**:
- This is expected - Docker uses `python-periphery` instead
- Dockerfile is already configured correctly
- If you see this error, rebuild: `docker-compose build --no-cache`

### Native LCD Issues

**Problem**: "No module named 'periphery'"  
**Solution**:
- Install correct package: `pip install python-periphery==2.4.1`
- Old package name was `periphery`, new one is `python-periphery`
- Update requirements.txt if needed

**Problem**: Display doesn't turn on  
**Solution**:
- Check all wiring connections (see wiring diagram)
- Verify SPI is enabled: `sudo raspi-config` → Interface Options → SPI → Enable
- Test with: `ls /dev/spidev*` (should show `/dev/spidev0.0`)
- Check power connections (VCC to 3.3V, not 5V!)

### General Issues

**Problem**: "Permission denied" when accessing GPIO  
**Solution**:
- Add user to gpio group: `sudo usermod -a -G gpio $USER`
- Logout and login again
- Or run with sudo (not recommended for production)

**Problem**: High CPU usage  
**Solution**:
- This is normal during ESP32 streaming (encoding RGB565)
- Reduce FPS in stats.py if needed (change `FPS = 30` to lower value)
- Native LCD mode uses less CPU than WiFi streaming

## Future Improvements

- **Backlight Control**: Move LED to GPIO for programmatic on/off
- **Configurable Timeout**: Settings screen for auto-off timers
- **Brightness Control**: PWM backlight dimming
- **Themes**: Multiple color palettes
- **Animated Transitions**: Smooth screen switching effects
- **ESP32 Battery Support**: Add battery monitoring and low-power modes
- **mDNS Discovery**: Auto-detect ESP32 displays on network
- **Multiple Displays**: Support streaming to multiple ESP32 devices

## Credits & Acknowledgments

This project was inspired by [mklements/OLED_Stats](https://github.com/mklements/OLED_Stats) — a great starting point for displaying system info on tiny screens. Big thanks for the spark!

### Coming Soon
- Photos of the panel running on Raspberry Pi
- Custom 3D-printed case STL files (free on Thingiverse)
- ESP32 enclosure design for standalone wireless display

## License

MIT License - see [LICENSE](LICENSE) file for details.