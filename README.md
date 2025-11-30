# Raspberry Pi System Monitor LCD Panel

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A multi-mode system monitor for Raspberry Pi with support for:
* **Direct LCD display** (ILI9163 via SPI)
* **ESP32 WiFi display** (remote wireless screen)
* **Windows simulation** (Tkinter GUI for development)

## Motivation

I recently got a Raspberry Pi 5 to set up my own home server. I'm hosting my website on it and have some exciting future projects lined up. I wanted a way to monitor system stats from my desk, so I developed this project to display important information like public IP, local IP, CPU temperature, memory usage, disk usage, and other metrics.

The app supports three display modes:
* **Native LCD**: Direct connection to ILI9163 display on Raspberry Pi
* **ESP32 WiFi**: Wireless streaming to an ESP32-C3 with LCD display
* **Simulation**: Windows development mode with Tkinter window

## Features

- **Real-time monitoring**:
  - Public & Local IP Addresses
  - CPU Usage & Temperature
  - Memory Utilization
  - Disk Space
  - System Uptime
  - Current Time
- **Multi-screen support** with button navigation
- **Three display modes:**:
  - Native SPI LCD (ILI9163)
  - WiFi streaming to ESP32
  - Desktop simulation (Windows/Tkinter)
- **Hardware acceleration** for SPI displays
- **Modular architecture**
  - Screen Management System
  - Hardware Abstraction Layer
  - Input Handling Framework

## Display Modes

1. **Native LCD (Raspberry Pi)**
  Direct SPI connection to 1.44" 128x128 ILI9163 display. Lowest latency, requires physical wiring.

2. **ESP32 WiFi Display**
  Stream display data over WiFi to an ESP32-C3 with attached LCD. Benefits:
    - No physical connection required
    - Flexible placement
    - Can be powered independently
    - Same visual output as native mode

3. **Windows Simulation**
  Development mode with Tkinter window showing what would appear on the LCD.

## Project Structure

The project is divided into several classes and modules to maintain code modularity and clarity:

```bash
lcdstats/
├── devices/
│   ├── device.py                 # Interface for devices that can display images
│   ├── fake_display.py           # Tkinter-based display simulator
│   ├── ILI9163.py                # ILI9163 LCD controller driver
│   └── esp32_wifi_display.py     # WiFi streaming client
├── esp32_display_server/         # ESP32 firmware (Arduino)
│   ├── config.h                  # WiFi & hardware config
│   ├── display.h/cpp             # ILI9163 driver for ESP32
│   ├── input.h/cpp               # Button handler
│   ├── network.h/cpp             # WiFi protocol
│   ├── state_manager.h/cpp       # Device state machine
│   ├── progress.h/cpp            # Progress indicator UI
│   └── esp32_display_server.ino  # Main firmware
├── fonts/                        # Custom fonts for display
├── resources/                    # Graphical assets (icons, sprites, GIFs)
├── tests/                        # Validation and QA tests
│   ├── resources/                # Test-specific assets
│   └── test_suite.py             # Runs multiple tests via an interactive CLI interface
├── utils/                        # Helper classes
│   └── progress_indicator.py     # A class to draw a circular progress indicator
├── views/                        # UI Screen implementations
│   ├── screen.py                 # Abstract Screen base class
│   ├── main_screen.py            # Primary system metrics display
│   └── secondary_screen.py       # Secondary media/animation display
├── data_gatherer.py              # System metrics collection module
├── input_handler.py              # GPIO/Tkinter input processor
├── screen_manager.py             # Screen state controller
├── stats.py                      # Main application entry point
├── Dockerfile                 # Docker container config
└── docker-compose.yml         # Docker orchestration
```

## Hardware Requirements

**Native LCD Setup (Raspberry Pi)**
| Component    | Specification                          |
| ------------ | -------------------------------------- |
| Raspberry Pi | Model 3B+/4/5 (Tested on Pi 5)         |
| Display      | 1.44" 128x128 SPI TFT (ILI9163 driver) |
| Button       | Momentary push button (Normally Open)  |

**ESP32 WiFi Display Setup**
| Component    | Specification                          |
| ------------ | -------------------------------------- |
| Raspberry Pi | Model 3B+/4/5 (runs Python client)     |
| ESP32        | ESP32-C3 or similar                    |
| Display      | 1.44" 128x128 SPI TFT (ILI9163 driver) |
| Button       | Momentary push button (Normally Open)  |


## Software Dependencies

```bash
# requirements.txt (Raspberry Pi)
Pillow==10.3.0      # Image processing
numpy==1.26.4       # Buffer management
periphery==2.1.1    # GPIO control
spidev==3.6         # SPI communication

# requirements-windows.txt
Pillow==10.3.0
numpy==1.26.4
tkinter==0.1.0      # GUI framework
```

## Wiring Diagrams

**Native LCD Mode (Raspberry Pi → ILI9163)**
|        Pin        | Physical Pin |  Raspberry Pi  | Function            |
| :---------------: | :----------: | :------------: | :------------------ |
|        VCC        |    Pin 1     |   3.3V Power   | Power supply (main) |
|        GND        |    Pin 6     |     Ground     | Common ground       |
|        SCL        |    Pin 23    | GPIO 11 (SCLK) | Clock SPI           |
|        SDA        |    Pin 19    | GPIO 10 (MOSI) | Data SPI            |
|    RES (Reset)    |    Pin 22    |    GPIO 25     | Display Reset       |
| DC (Data/Command) |    Pin 18    |    GPIO 24     | Data/Command Select |
|        CS         |    Pin 29    |     GPIO 5     | Chip Select         |
|        LED        |    Pin 17    |   3.3V Power   | Backlight Power     |
|   Button Signal   |    Pin 12    |    GPIO 18     | Button input        |
|   Button Ground   |    Pin 9     |     Ground     | Button return path  |

**ESP32 WiFi Mode (ESP32-C3 → ILI9163)**
|        Pin        | ESP32-C3 GPIO | Function            |
| :---------------: | :-----------: | :------------------ |
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

Note: ESP32 button uses internal pull-up, no external resistor needed.

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
*⚠️ Important Note on Docker Mode:*
When running in Docker, the app **cannot access real system metrics** (CPU temp, memory usage, etc.) because it's isolated in a container. Docker mode is primarily useful for:

* **ESP32 WiFi display**: Stream to remote display (works perfectly)
* **Development/Testing**: Simulated data for UI testing
* **Portability**: Easy deployment without system dependencies

**For native LCD with real metrics**, use native installation (Option 1).

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

1. **Configure WiFi** in `esp32_display_server/config.h`:
   ```cpp
   #define WIFI_SSID "YourNetworkName"
   #define WIFI_PASSWORD "YourPassword"
   
   // Optional: Set static IP
   #define STATIC_IP_ENABLED true
   #define STATIC_IP_3 199  // Last octet (192.168.0.199)
   ```

2. **Upload firmware**:
   - Open `esp32_display_server.ino` in Arduino IDE
   - Select board: ESP32-C3 Dev Module
   - Install required libraries: ArduinoJson
   - Upload to ESP32

3. **Note the IP address** shown on ESP32 display after boot

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
- Check WiFi credentials in `config.h`
- Verify ESP32 and Raspberry Pi are on same network
- Check firewall rules (port 8080)

**Problem**: Display freezes or shows artifacts  
**Solution**:
- Check SPI connections (loose wires)
- Reduce SPI frequency in `config.h` if needed
- Verify power supply stability (use quality USB cable)

**Problem**: "Connection failed" errors in Python  
**Solution**:
- Verify ESP32 IP address with `ping <esp32-ip>`
- Check ESP32 serial output for errors
- Restart ESP32 (power cycle)

### Docker Mode Issues

**Problem**: Cannot connect to ESP32  
**Solution**:
- Use `--network host` mode (already in docker-compose)
- Verify ESP32 IP is reachable from host
- Check environment variable `ESP32_HOST` is correct

**Problem**: System metrics show simulated data  
**Solution**:
- This is expected behavior in Docker
- For real metrics, use native installation with `--display raspberry`

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
- Photos of the ESP32 screen running thru wifi
- Custom 3D-printed case STL files (free on Thingiverse) Both standalone and wired versions

## License

MIT License - see [LICENSE](LICENSE) file for details.
