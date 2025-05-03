from PIL import ImageFont
from views.screen import Screen
from data_gatherer import DataGatherer
import time

class MainScreen(Screen):
    DATA_UPDATE_INTERVAL = 1.0  # seconds
    DEFAULT_COLOR = (255, 255, 255)
    
    # Temperature thresholds
    MIN_TEMP = 40.0
    IDLE_TEMP = 50.0
    MAX_TEMP = 80.0
    
    # Layout constants
    LINE_Y_POSITIONS = [43, 85]
    ICON_POSITIONS = {
        "temp": (2, 3),
        "mem": (67, 3),
        "disk": (2, 23),
        "cpu": (67, 23),
        "wifi": (2, 45),
        "eth": (2, 65),
        "uptime": (2, 87),
        "time": (2, 107)
    }
    TEXT_POSITIONS = {
        "temp": (19, 3),
        "mem": (87, 3),
        "disk": (19, 23),
        "cpu": (87, 23),
        "local_ip": (21, 45),
        "public_ip": (21, 65),
        "uptime": (21, 87),
        "time": (21, 107)
    }
    ICON_CODES = {
        "temp": chr(63339),
        "mem": chr(62776),
        "disk": chr(63426),
        "cpu": chr(62171),
        "wifi": chr(61931),
        "eth": chr(63382),
        "uptime": chr(62034),
        "time": chr(61463)
    }

    def __init__(self, is_raspberry: bool, screen_width: int, screen_height: int):
        super().__init__(is_raspberry, screen_width, screen_height)
        self.data_gatherer = DataGatherer(is_raspberry)

        self.font = ImageFont.truetype('fonts/PixelOperator.ttf', 16)
        self.icon_font = ImageFont.truetype('fonts/lineawesome-webfont.ttf', 18)

        self.last_data_update = 0.0
        self.data = {}
        self.data_values = {}

        self.refresh_data()

    def refresh_data(self):
        self.data = {
            "public_ip": self.data_gatherer.get_public_ip(),
            "local_ip": self.data_gatherer.get_local_ip(),
            "cpu": self.data_gatherer.get_cpu_usage(),
            "mem": self.data_gatherer.get_mem_usage(),
            "disk": self.data_gatherer.get_disk_usage(),
            "temp": self.data_gatherer.get_temperature(),
            "uptime": self.data_gatherer.get_uptime(),
            "time": self.data_gatherer.get_systime()
        }
        self.data_values = {
            "cpu": self.data_gatherer.get_cpu_usage_value() / 100.0,
            "mem": self.data_gatherer.get_mem_usage_value() / 100.0,
            "disk": self.data_gatherer.get_disk_usage_value() / 100.0,
            "temp": self.data_gatherer.get_temperature_value()
        }

    def update(self, delta: float):
        self.last_data_update += delta
        if self.last_data_update >= self.DATA_UPDATE_INTERVAL:
            self.last_data_update = 0.0
            self.refresh_data()

    @staticmethod
    def get_color_by_percentage(percentage: float):
        percentage = max(0.0, min(1.0, percentage))
        red = int(255 * percentage)
        green = int(255 * (1 - percentage))
        pastel_red = (red + 255) // 2
        pastel_green = (green + 255) // 2
        return (pastel_red, pastel_green, 127)

    def get_color_by_temperature(self, temperature: float):
        min_idle = self.IDLE_TEMP - self.MIN_TEMP
        idle_max = self.MAX_TEMP - self.IDLE_TEMP

        if temperature < self.MIN_TEMP:
            t = (self.MIN_TEMP - max(temperature, 2 * self.MIN_TEMP - self.IDLE_TEMP)) / min_idle
            red, green = 0, int(255 - 127 * max(0.0, min(1.0, t)))
        elif temperature <= self.IDLE_TEMP:
            red = int(255 * (temperature - self.MIN_TEMP) / min_idle)
            green = 255
        elif temperature <= self.MAX_TEMP:
            green = int(255 * (1 - (temperature - self.IDLE_TEMP) / idle_max))
            red = 255
        else:
            red, green = 255, 0

        return ((red + 255) // 2, (green + 255) // 2, 127)

    def draw(self, draw, image):
        draw.rectangle((0, 0, self.screen_width, self.screen_height), outline=0, fill=0)

        temp_color = self.get_color_by_temperature(self.data_values["temp"])
        mem_color = self.get_color_by_percentage(self.data_values["mem"])
        disk_color = self.get_color_by_percentage(self.data_values["disk"])
        cpu_color = self.get_color_by_percentage(self.data_values["cpu"])

        # Icons
        draw.text(self.ICON_POSITIONS["temp"], self.ICON_CODES["temp"], font=self.icon_font, fill=temp_color)
        draw.text(self.ICON_POSITIONS["mem"], self.ICON_CODES["mem"], font=self.icon_font, fill=mem_color)
        draw.text(self.ICON_POSITIONS["disk"], self.ICON_CODES["disk"], font=self.icon_font, fill=disk_color)
        draw.text(self.ICON_POSITIONS["cpu"], self.ICON_CODES["cpu"], font=self.icon_font, fill=cpu_color)
        draw.text(self.ICON_POSITIONS["wifi"], self.ICON_CODES["wifi"], font=self.icon_font, fill=self.DEFAULT_COLOR)
        draw.text(self.ICON_POSITIONS["eth"], self.ICON_CODES["eth"], font=self.icon_font, fill=self.DEFAULT_COLOR)
        draw.text(self.ICON_POSITIONS["uptime"], self.ICON_CODES["uptime"], font=self.icon_font, fill=self.DEFAULT_COLOR)
        draw.text(self.ICON_POSITIONS["time"], self.ICON_CODES["time"], font=self.icon_font, fill=self.DEFAULT_COLOR)

        # Lines
        for y in self.LINE_Y_POSITIONS:
            draw.line([(0, y), (self.screen_width, y)], fill=self.DEFAULT_COLOR, width=0)

        # Texts
        draw.text(self.TEXT_POSITIONS["temp"], self.data["temp"], font=self.font, fill=temp_color)
        draw.text(self.TEXT_POSITIONS["mem"], self.data["mem"], font=self.font, fill=mem_color)
        draw.text(self.TEXT_POSITIONS["disk"], self.data["disk"], font=self.font, fill=disk_color)
        draw.text(self.TEXT_POSITIONS["cpu"], self.data["cpu"], font=self.font, fill=cpu_color)
        draw.text(self.TEXT_POSITIONS["local_ip"], self.data["local_ip"], font=self.font, fill=self.DEFAULT_COLOR)
        draw.text(self.TEXT_POSITIONS["public_ip"], self.data["public_ip"], font=self.font, fill=self.DEFAULT_COLOR)
        draw.text(self.TEXT_POSITIONS["uptime"], self.data["uptime"], font=self.font, fill=self.DEFAULT_COLOR)
        draw.text(self.TEXT_POSITIONS["time"], self.data["time"], font=self.font, fill=self.DEFAULT_COLOR)