from PIL import ImageFont
from views.screen import Screen
from data_gatherer import DataGatherer

class MainScreen(Screen):
    # Default data gathering interval in seconds
    DATA_UPDATE_INTERVAL = 1.0

    # Default drawing color (in this case, white)
    DEFAULT_COLOR = (255, 255, 255)

    # Raspberry PI 5 temp. reference values.
    MIN_TEMP = 40.0  # This, or less is very good.
    IDLE_TEMP = 50.0  # Usual idle temp with oficial active cooler
    MAX_TEMP = 80.0  # When the CPU reaches 80°C, it will begin to throttle, reducing the CPU and GPU frequencies.

    def __init__(self):
        self.data_gatherer = DataGatherer()
        self.is_raspberry = False
        self.screen_width = 0
        self.screen_height = 0
        self.last_data_update = 0.0
        
        self.PublicIP = ""
        self.LocalIP = ""
        self.CPU = ""
        self.MemUsage = ""
        self.Disk = ""
        self.Temperature = ""
        self.uptime = ""
        self.systime = ""
        
        self.CPU_value = 0
        self.MemUsage_value = 0
        self.Disk_value = 0
        self.Temperature_value = 0

        self.font = ImageFont.truetype('fonts/PixelOperator.ttf', 16)
        self.icon_font = ImageFont.truetype('fonts/lineawesome-webfont.ttf', 18)
        
    def init(self, is_raspberry, screen_width, screen_height):
        self.data_gatherer.is_raspberry = is_raspberry
        self.is_raspberry = is_raspberry
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.last_data_update = self.DATA_UPDATE_INTERVAL
        self.refresh_data()

    def refresh_data(self):
        self.PublicIP = self.data_gatherer.get_public_ip()
        self.LocalIP = self.data_gatherer.get_local_ip()
        self.CPU = self.data_gatherer.get_cpu_usage()
        self.MemUsage = self.data_gatherer.get_mem_usage()
        self.Disk = self.data_gatherer.get_disk_usage()
        self.Temperature = self.data_gatherer.get_temperature()
        self.uptime = self.data_gatherer.get_uptime()
        self.systime = self.data_gatherer.get_systime()
        self.CPU_value = self.data_gatherer.get_cpu_usage_value() / 100.0
        self.MemUsage_value = self.data_gatherer.get_mem_usage_value() / 100.0
        self.Disk_value = self.data_gatherer.get_disk_usage_value() / 100.0
        self.Temperature_value = self.data_gatherer.get_temperature_value()

    def update(self, delta):
        self.last_data_update += delta
        if self.last_data_update >= self.DATA_UPDATE_INTERVAL:
            self.last_data_update = 0.0
            self.refresh_data()

    @staticmethod
    def get_color_by_percentage(percentage: float):
        percentage = max(0.0, min(1.0, percentage))
        red = int(255 * percentage)
        green = int(255 * (1 - percentage))
        blue = 0

        pastel_red = int((red + 255) / 2)
        pastel_green = int((green + 255) / 2)
        pastel_blue = int((blue + 255) / 2)

        return (pastel_red, pastel_green, pastel_blue)

    def get_color_by_temperature(self, temperature: float):
        min_idle = self.IDLE_TEMP - self.MIN_TEMP
        idle_max = self.MAX_TEMP - self.IDLE_TEMP
        
        if temperature < self.MIN_TEMP:
            t = (self.MIN_TEMP - max(temperature, 2*self.MIN_TEMP - self.IDLE_TEMP)) / min_idle
            red, green = 0, int(255 - 127 * max(0.0, min(1.0, t)))
        elif temperature <= self.IDLE_TEMP:
            red = int(255 * (temperature - self.MIN_TEMP)/min_idle)
            green = 255
        elif temperature <= self.MAX_TEMP:
            green = int(255 * (1 - (temperature - self.IDLE_TEMP)/idle_max))
            red = 255
        else:
            red, green = 255, 0

        return ((red + 255) // 2, (green + 255) // 2, 127)

    def draw(self, draw, image):
        draw.rectangle((0, 0, self.screen_width, self.screen_height), outline=0, fill=0)

        draw.text((2,  3), chr(63339), font=self.icon_font, fill=self.get_color_by_temperature(self.Temperature_value)) # Icon temperature
        draw.text((67, 3), chr(62776), font=self.icon_font, fill=self.get_color_by_percentage(self.MemUsage_value)) # Icon memory
        draw.text((2,  23), chr(63426), font=self.icon_font, fill=self.get_color_by_percentage(self.Disk_value)) # Icon disk
        draw.text((67, 23), chr(62171), font=self.icon_font, fill=self.get_color_by_percentage(self.CPU_value)) # Icon cpu
        draw.line([(0, 43), (128, 43)], fill=self.DEFAULT_COLOR, width=0)
        draw.text((2,  45), chr(61931), font=self.icon_font, fill=self.DEFAULT_COLOR) # Icon wifi
        draw.text((2,  65), chr(63382), font=self.icon_font, fill=self.DEFAULT_COLOR) # Icon ethernet
        draw.line([(0, 85), (128, 85)], fill=self.DEFAULT_COLOR, width=0)
        draw.text((2,  87), chr(62034), font=self.icon_font, fill=self.DEFAULT_COLOR) # Icon hourglass
        draw.text((2,  107), chr(61463), font=self.icon_font, fill=self.DEFAULT_COLOR) # Icon clock

        draw.text((19, 3), self.Temperature, font=self.font, fill=self.get_color_by_temperature(self.Temperature_value))
        draw.text((87, 3), self.MemUsage, font=self.font, fill=self.get_color_by_percentage(self.MemUsage_value))
        draw.text((19, 23), self.Disk, font=self.font, fill=self.get_color_by_percentage(self.Disk_value))
        draw.text((87, 23), self.CPU, font=self.font, fill=self.get_color_by_percentage(self.CPU_value))
        draw.text((21, 45), self.LocalIP, font=self.font, fill=self.DEFAULT_COLOR)
        draw.text((21, 65), self.PublicIP, font=self.font, fill=self.DEFAULT_COLOR)
        draw.text((21, 87), self.uptime, font=self.font, fill=self.DEFAULT_COLOR)
        draw.text((21, 107), self.systime, font=self.font, fill=self.DEFAULT_COLOR)