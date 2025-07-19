from PIL.ImageDraw import ImageDraw

from widget import Widget
from component.text import Font, draw_text
from component.pill import draw_vertical_pill
from component.icon import draw_icon
from component.curve import draw_curve


MARGIN = 6


class WidgetWeather3x4(Widget):
    name = "weather-3x4"
    width = 383
    height = 223

    @classmethod
    def draw(cls, draw: ImageDraw):
        draw_text(draw, (MARGIN, MARGIN), Font.MEDIUM, "Aujourd'hui")
        draw_text(draw, (50, 15), Font.XLARGE, "24°")
        draw_icon(draw, (10, 35), "large-sun")

        draw_vertical_pill(draw, (170, 13, 176, 38), 0.9)
        draw_text(draw, (180, 10), Font.SMALL, "Extrèmes")
        draw_text(draw, (180, 18), Font.LARGE, "17°-24°")

        draw_text(draw, (180, 50), Font.SMALL, "Ressenti")
        draw_text(draw, (180, 58), Font.LARGE, "27°")

        draw_text(draw, (280, 10), Font.SMALL, "Lever du Soleil")
        draw_text(draw, (280, 18), Font.LARGE, "06:53")

        draw_text(draw, (280, 50), Font.SMALL, "Coucher du Soleil")
        draw_text(draw, (280, 58), Font.LARGE, "19:35")

        def temp_func(hour: float) -> float:
            return 30.0 - ((hour - 17) ** 2) / 24.0

        draw_curve(
            draw,
            (10, 90, cls.width - 10, 150),
            lambda x: temp_func(x * 24.0) / 30.0,
            0.1,
        )

        for time in range(0, 25, 2):
            spacing = (cls.width - 2 * MARGIN) // 12 - 1
            x = MARGIN + time * spacing // 2
            draw_text(draw, (x, 160), Font.SMALL, f"{time:02}h")
            draw_text(draw, (x, 178), Font.SMALL, f"{int(temp_func(time))}°")
            draw_icon(draw, (x, 195), "small-sun")
            draw_text(draw, (x, 210), Font.SMALL, "30%")
