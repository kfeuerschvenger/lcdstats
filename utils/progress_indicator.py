from PIL import Image, ImageDraw
from typing import Optional

class ProgressIndicator:
    """A class to draw a circular progress indicator with a glow effect and dynamic border color."""
    
    # Constants
    _MIN_DRAW_TIME = 0.2
    _FULL_CIRCLE = 360
    _START_ANGLE = -90
    _GLOW_ALPHA_BASE = 60
    _BORDER_ALPHA = 200
    _FINAL_ARC_ALPHA = 255

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize the ProgressIndicator with default or custom configuration."""
        self.config = {
            'outer_radius': 12,
            'inner_radius': 8,
            'margin': 10,
            'outline_width': 2,
            'glow_steps': 3,
            'bg_color': (30, 30, 30, 100),
            'start_color': (255, 0, 0),      # Red
            'end_color': (0, 255, 0),        # Green
            'dynamic_border': True,
            **(config or {})
        }

    def draw(self, base_image: Image.Image, elapsed_time: float, max_time: float) -> None:
        """Draw the progress indicator on the base image."""
        if not self._MIN_DRAW_TIME < elapsed_time < max_time:
            return

        progress = elapsed_time / max_time
        cfg = self.config
        w, h = base_image.size

        # Indicator position: bottom-right corner
        x = w - cfg['outer_radius'] - cfg['margin']
        y = h - cfg['outer_radius'] - cfg['margin']

        # Create transparent overlay
        overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        self._draw_background(draw, x, y)
        self._draw_progress(draw, x, y, progress)
        self._draw_border(draw, x, y, progress)

        base_image.alpha_composite(overlay)

    def _draw_background(self, draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
        """Draw the background circle"""
        r = self.config['outer_radius']
        box = (x - r, y - r, x + r, y + r)
        draw.ellipse(box, fill=self.config['bg_color'])

    def _interpolate_color(self, start: tuple, end: tuple, t: float) -> tuple:
        """Interpolate between two RGB colors based on the progress."""
        # Linear interpolation of RGB values
        return tuple(int(s + (e - s) * t) for s, e in zip(start, end))

    def _draw_progress(self, draw: ImageDraw.ImageDraw, x: int, y: int, progress: float) -> None:
        """Draw the progress arc with glow effect."""
        cfg = self.config
        r = cfg['inner_radius']
        box = (x - r, y - r, x + r, y + r)
        end_angle = self._START_ANGLE + (self._FULL_CIRCLE * progress)

        color = self._interpolate_color(cfg['start_color'], cfg['end_color'], progress)

        # Draw glow effect in layers
        for i in range(cfg['glow_steps'], 0, -1):
            alpha = int(self._GLOW_ALPHA_BASE * (i / cfg['glow_steps']))
            width = cfg['outline_width'] + i
            draw.arc(box, self._START_ANGLE, end_angle, fill=(*color, alpha), width=width)

        # Final solid arc
        draw.arc(box, self._START_ANGLE, end_angle, fill=(*color, self._FINAL_ARC_ALPHA), width=cfg['outline_width'])

    def _draw_border(self, draw: ImageDraw.ImageDraw, x: int, y: int, progress: float) -> None:
        """Draw the border arc with dynamic color."""
        cfg = self.config
        r = cfg['inner_radius']
        box = (x - r, y - r, x + r, y + r)

        color = (
            self._interpolate_color(cfg['start_color'], cfg['end_color'], progress)
            if cfg['dynamic_border']
            else cfg['start_color']
        )

        draw.arc(box, 0, self._FULL_CIRCLE, fill=(*color, self._BORDER_ALPHA), width=1)