from PIL import ImageFont, Image, ImageDraw
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from data_gatherer import DataGatherer
from views.screen import Screen

Color = Tuple[int, int, int, int] # RGBA color type

@dataclass
class IconConfig:
    """Configuration for icons on the screen."""
    position: Tuple[int, int]
    color: Optional[Color]
    has_effects: bool = True

class MainScreen(Screen):
    """Main screen class for displaying system information."""
    DATA_UPDATE_INTERVAL = 1.0 # seconds
    DEFAULT_COLOR: Color = (255, 255, 255, 255)
    TEXT_SHADOW_OFFSET = (1, 1)
    EFFECT_ALPHA = 100

    MIN_TEMP, IDLE_TEMP, MAX_TEMP = 40.0, 50.0, 80.0 # degrees Celsius
    LINE_Y_POSITIONS = [43, 85] # Y positions for horizontal lines

    ICON_CONFIG: Dict[str, IconConfig] = {
        "temp": IconConfig((2, 3), None),
        "mem": IconConfig((67, 3), None),
        "disk": IconConfig((2, 23), None),
        "cpu": IconConfig((67, 23), None),
        "wifi": IconConfig((2, 45), DEFAULT_COLOR, False),
        "eth": IconConfig((2, 65), DEFAULT_COLOR, False),
        "uptime": IconConfig((2, 87), DEFAULT_COLOR, False),
        "time": IconConfig((2, 107), DEFAULT_COLOR, False),
    }

    TEXT_POSITIONS = {
        "temp": (19, 3), "mem": (87, 3),
        "disk": (19, 23), "cpu": (87, 23),
        "local_ip": (21, 45), "public_ip": (21, 65),
        "uptime": (21, 87), "time": (21, 107)
    }

    ICON_CODES = {
        "temp": chr(63339), "mem": chr(62776), "disk": chr(63426),
        "cpu": chr(62171), "wifi": chr(61931), "eth": chr(63382),
        "uptime": chr(62034), "time": chr(61463)
    }

    def __init__(self, is_raspberry: bool, screen_width: int, screen_height: int) -> None:
        """Initializes the main screen with the given parameters."""
        super().__init__(is_raspberry, screen_width, screen_height)
        self.data_gatherer = DataGatherer(is_raspberry)
        self.font = self._load_font('fonts/PixelOperator.ttf', 16)
        self.icon_font = self._load_font('fonts/lineawesome-webfont.ttf', 18)
        self.last_data_update = 0.0
        self.data, self.data_values = {}, {}
        self.refresh_data()

    def _load_font(self, path: str, size: int) -> ImageFont.FreeTypeFont:
        """Loads a font from the specified path."""
        return ImageFont.truetype(path, size)

    def refresh_data(self) -> None:
        """Refreshes the data from the data gatherer."""
        g = self.data_gatherer
        self.data = {
            "public_ip": g.get_public_ip(), "local_ip": g.get_local_ip(),
            "cpu": g.get_cpu_usage(), "mem": g.get_mem_usage(),
            "disk": g.get_disk_usage(), "temp": g.get_temperature(),
            "uptime": g.get_uptime(), "time": g.get_systime()
        }
        self.data_values = {k: g.get_metric_value(k) for k in ['cpu', 'mem', 'disk', 'temp']}

    def update(self, delta: float) -> None:
        """Updates the screen with new data if the interval has passed."""
        self.last_data_update += delta
        if self.last_data_update >= self.DATA_UPDATE_INTERVAL:
            self.last_data_update = 0.0
            self.refresh_data()

    def _calculate_colors(self) -> Dict[str, Color]:
        return {
            "temp": self._color_by_temp(self.data_values["temp"]),
            "mem": self._color_by_percent(self.data_values["mem"]),
            "disk": self._color_by_percent(self.data_values["disk"]),
            "cpu": self._color_by_percent(self.data_values["cpu"])
        }

    @staticmethod
    def _color_by_percent(p: float) -> Color:
        """Calculates color based on percentage."""
        p = max(0.0, min(1.0, p))
        r, g = int(255 * p), int(255 * (1 - p))
        return ((r + 255) // 2, (g + 255) // 2, 127, 255)

    def _color_by_temp(self, t: float) -> Color:
        """Calculates color based on temperature."""
        min_idle = self.IDLE_TEMP - self.MIN_TEMP
        idle_max = self.MAX_TEMP - self.IDLE_TEMP

        if t < self.MIN_TEMP:
            ratio = (self.MIN_TEMP - max(t, 2 * self.MIN_TEMP - self.IDLE_TEMP)) / min_idle
            r, g = 0, int(255 - 127 * max(0.0, min(1.0, ratio)))
        elif t <= self.IDLE_TEMP:
            r = int(255 * (t - self.MIN_TEMP) / min_idle)
            g = 255
        elif t <= self.MAX_TEMP:
            r = 255
            g = int(255 * (1 - (t - self.IDLE_TEMP) / idle_max))
        else:
            r, g = 255, 0

        return ((r + 255) // 2, (g + 255) // 2, 127, 255)

    def draw(self, draw: ImageDraw.ImageDraw, image: Image.Image) -> None:
        """Draws the main screen with icons and text."""
        draw.rectangle((0, 0, self.screen_width, self.screen_height), outline=0, fill=0)
        colors = self._calculate_colors()

        for icon, config in self.ICON_CONFIG.items():
            color = colors.get(icon, config.color or self.DEFAULT_COLOR)
            self._draw_icon(draw, icon, config.position, color, config.has_effects)

        for y in self.LINE_Y_POSITIONS:
            draw.line([(0, y), (self.screen_width, y)], fill=self.DEFAULT_COLOR)

        for k in ['temp', 'mem', 'disk', 'cpu']:
            draw.text(self.TEXT_POSITIONS[k], self.data[k], font=self.font, fill=colors[k])

        for k in ['local_ip', 'public_ip', 'uptime', 'time']:
            draw.text(self.TEXT_POSITIONS[k], self.data[k], font=self.font, fill=self.DEFAULT_COLOR)

    def _draw_icon(self, draw: ImageDraw.ImageDraw, key: str, pos: Tuple[int, int], color: Color, fx: bool) -> None:
        """Draws the icon at the specified position with the given color and effects."""
        if fx:
            shadow = tuple(p + o for p, o in zip(pos, self.TEXT_SHADOW_OFFSET))
            shadow = (shadow[0], shadow[1]) # Ensure shadow is within bounds
            self._draw_text(draw, shadow, self.ICON_CODES[key], (*color[:3], 60))
        self._draw_text(draw, pos, self.ICON_CODES[key], color)

    def _draw_text(self, draw: ImageDraw.ImageDraw, pos: Tuple[int, int], text: str, color: Color) -> None:
        """Draws text at the specified position with the given color."""
        draw.text(pos, text, font=self.icon_font, fill=color)