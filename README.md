# LCD Information Panel Project

The script is pre-configured for 128x128 LCD Display, but can easily be modified

## Motivation

I recently got a Raspberry Pi 5 to set up my own home server. I’m hosting my website on it and have some exciting future projects lined up to host there as well. So, I thought it would be both important (and, let’s be honest, fun) to add a small screen to check the status of my Raspberry from the comfort of my desk. To do that, I developed this small project, which shows important information like public IP, local IP, CPU temperature, memory usage, disk usage, and other related data.

This little app is designed to run on my PC in simulation mode to fine-tune everything, showing what would be displayed on the screen in a window. When running on the Raspberry Pi, it shows the data on the connected screen.

## Project Structure

The project is divided into several classes and modules to maintain code modularity and clarity:

```
lcdstats/
├── fonts/
├── resources/
├── views/
│   ├── screen.py
│   ├── main_screen.py
│   └── secondary_screen.py
├── data_gatherer.py
├── fake_display.py
├── input_handler.py
├── screen_manager.py
└── stats.py
```

## Directory "views/"

**screen.py:** Defines the base class Screen, which provides the basic structure for all screens. Classes inheriting from Screen must implement the update and draw methods to define how they update and draw the screen.

**main_screen.py:** The MainScreen class inherits from Screen and is responsible for displaying system data, such as public IP, local IP, CPU, memory, disk, temperature, uptime, and system time. The data is updated periodically every second and displayed on the LCD screen.

**secondary_screen.py:** The SecondaryScreen class also inherits from Screen and is responsible for displaying an animation in GIF format. The GIF is resized and drawn frame by frame on the LCD screen.

## Directory "/"

**data_gatherer.py:** Is responsible for collecting system data such as public IP, local IP, CPU usage, memory usage, disk usage, temperature, uptime, and system time. Also provides simulated data for simulation environment.

**fake_display.py:** Simulates the behavior of the LCD screen on a non-Raspberry Pi environment, allowing you to test and visualize the panel's functionality on a regular computer.

**input_handler.py:** Handles user input, such as button presses or key events. In the case of simulation on Windows, it uses Tkinter events to manage interactions, while on the Raspberry Pi, it interfaces with physical buttons or other input devices.

**screen_manager.py:** Manages the transitions and switching between different screens in the LCD panel system.

**stats.py:** Serves as the entry point of the application. It contains the main loop that is responsible for continuously updating the necessary system data and rendering the relevant information to the display.

## My Hardware:

- Raspberry Pi 5 model B
- LCD 1.44" Serial 128X128 SPI Color TFT. Drive IC: ILI9163

## Libraries:

- PIL (Pillow) for image manipulation
- tkinter (only for simulation on Windows)

## Wiring:

|      Display      |   Raspberry (GPIO)   |               Function                |
| :---------------: | :------------------: | :-----------------------------------: |
|        VCC        |     Pin 1 (3.3V)     |            Positive supply            |
|        GND        |     Pin 6 (GND)      |                Ground                 |
|        SCL        | Pin 23 (GPIO11/SCLK) |               Clock SPI               |
|        SDA        | Pin 19 (GPIO10/MOSI) |               Data SPI                |
|    RES (Reset)    |   Pin 22 (GPIO25)    |                 Reset                 |
| DC (Data/Command) |   Pin 18 (GPIO24)    | Indicates if sending data or commands |
|        CS         |  Pin 24 (GPIO8/CE0)  |            Chip Select SPI            |

## Installation

1. **Clone the repository:**

```
git clone <repository-url>
cd <repository-name>
```

2. **Install dependencies:**

Make sure you have Python 3 installed. Then, install the required dependencies:

```
pip install pillow
```

3. **Run the app**

   - **Run on Windows (simulation mode):**

   If you are using Windows to simulate the panel in a Tkinter window, you can run the following command:

   ```
   py stats.py
   ```

   - **Run on Raspberry Pi:**

   On the Raspberry Pi, I have Ubuntu Server 24.10 installed on it. I just installed python:

   ```
   sudo apt-get update
   sudo apt install python3-venv python3-pip
   ```

   Then I had to create a virtual environment called stats_env.

   ```
   python3 -m venv stats_env
   ```

   To activate the virtual environment:

   ```
   source lcd-env/bin/activate
   ```
