# Raspberry Pi System Monitor LCD Panel

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A dual-mode system monitor for Raspberry Pi with real LCD display support (ILI9163) and Windows simulation mode.

## Motivation

I recently got a Raspberry Pi 5 to set up my own home server. I’m hosting my website on it and have some exciting future projects lined up to host there as well. So, I thought it would be both important (and, let’s be honest, fun) to add a small screen to check the status of my Raspberry from the comfort of my desk. To do that, I developed this small project, which shows important information like public IP, local IP, CPU temperature, memory usage, disk usage, and other related data.

This little app is designed to run on my PC in simulation mode to fine-tune everything, showing what would be displayed on the screen in a window. When running on the Raspberry Pi, it shows the data on the connected screen.

## Features

- **Real-time monitoring**:
  - Public & Local IP Addresses
  - CPU Usage & Temperature
  - Memory Utilization
  - Disk Space
  - System Uptime
  - Current Time
- **Multi-screen support**
- **Cross-platform compatibility**:
  - Native Raspberry Pi operation (Ubuntu Server 24.10)
  - Windows simulation mode (Tkinter GUI)
- **Hardware acceleration** for SPI displays
- **Modular architecture**
  - Screen Management System
  - Hardware Abstraction Layer
  - Input Handling Framework

## Project Structure

The project is divided into several classes and modules to maintain code modularity and clarity:

```
lcdstats/
├── fonts/                     # Custom fonts for display
├── resources/                 # Graphical assets (icons, sprites, GIFs)
├── tests/                     # Validation and QA tests
│   ├── resources/             # Test-specific assets
│   └── test_suite.py          # Runs multiple tests via an interactive CLI interface
├── views/                     # UI Screen implementations
│   ├── screen.py              # Abstract Screen base class
│   ├── main_screen.py         # Primary system metrics display
│   └── secondary_screen.py    # Secondary media/animation display
├── data_gatherer.py           # System metrics collection module
├── fake_display.py            # Tkinter-based display simulator
├── ILI9163.py                 # ILI9163 LCD controller driver
├── input_handler.py           # GPIO/Tkinter input processor
├── screen_manager.py          # Screen state controller
└── stats.py                   # Main application entry point
```

## Hardware Requirements

| Component    | Specification                          |
| ------------ | -------------------------------------- |
| Raspberry Pi | Model 3B+/4/5 (Tested on Pi 5)         |
| Display      | 1.44" 128x128 SPI TFT (ILI9163 driver) |
| Button       | Momentary push button (Normally Open)  |

## Software Dependencies

```
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

## Wiring Diagram

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

## Installation

**Raspberry Pi Setup**

```
# 1. Install system dependencies
sudo apt update && sudo apt install -y \
  python3-dev \
  libgpiod-dev \
  libjpeg-dev \
  zlib1g-dev \
  python3-spidev

# 2. Create and activate virtual environment
python3 -m venv stats_env
source stats_env/bin/activate

# 3. Install Python packages
pip install -r requirements.txt
```

**Windows simulation Setup**

```
# 1. Create virtual environment
python -m venv stats_env
stats_env\Scripts\activate

# 2. Install dependencies
pip install -r requirements-windows.txt
```

## Usage

```
source stats_env/bin/activate
python3 stats.py
```

## Run tests

```
python test_suite.py           # Interactive menu
python test_suite.py all       # Run all tests
python test_suite.py image     # Run a specific test
```
