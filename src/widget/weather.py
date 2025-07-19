from PIL.ImageDraw import ImageDraw

from widget import Widget
from component.text import Font, draw_text
from component.pill import draw_vertical_pill
from component.icon import draw_icon
from component.curve import draw_curve
from metric.weather import MetricWeather


MARGIN = 6


class WidgetWeather3x4(Widget):
    name = "weather-3x4"
    width = 383
    height = 223

    @classmethod
    def draw(cls, draw: ImageDraw, weather: MetricWeather):
        temp_min = min(min(x.temperature for x in weather.hourly), weather.temperature)
        temp_max = max(max(x.temperature for x in weather.hourly), weather.temperature)

        draw_text(draw, (MARGIN, MARGIN), Font.MEDIUM, "Aujourd'hui")
        draw_text(draw, (50, 15), Font.XLARGE, f"{round(weather.temperature)}°")
        draw_icon(draw, (10, 35), "large-clear")

        # Section: min & max temperature
        draw_vertical_pill(
            draw,
            (170, 13, 176, 38),
            (weather.temperature - temp_min) / (temp_max - temp_min),
        )

        draw_text(draw, (180, 10), Font.SMALL, "Extrêmes")
        draw_text(draw, (180, 18), Font.LARGE, f"{round(temp_min)}°-{round(temp_max)}°")

        # Section: apparent temperature
        draw_text(draw, (180, 50), Font.SMALL, "Ressenti")

        draw_text(
            draw, (180, 58), Font.LARGE, f"{round(weather.temperature_apparent)}°"
        )

        # Section: sun events
        draw_text(draw, (280, 10), Font.SMALL, "Lever du Soleil")
        draw_text(draw, (280, 18), Font.LARGE, weather.sunrise.isoformat("minutes"))
        draw_text(draw, (280, 50), Font.SMALL, "Coucher du Soleil")
        draw_text(draw, (280, 58), Font.LARGE, weather.sunset.isoformat("minutes"))

        # Section: hourly
        def temp_func(hour: float) -> float:
            prev_val = weather.hourly[int(hour)].temperature

            if hour < 24.0:
                next_val = weather.hourly[int(hour) + 1].temperature
            else:
                next_val = prev_val

            alpha = hour % 1.0
            val = next_val * alpha + prev_val * (1.0 - alpha)
            return 0.1 + 0.9 * (val - temp_min) / (temp_max - temp_min)

        draw_curve(
            draw,
            (14, 90, cls.width - 14, 150),
            lambda x: temp_func(x * 24.0),
            (60.0 * weather.time.hour + weather.time.minute) / (24.0 * 60.0),
        )

        for time in range(0, 25, 2):
            x = 14 + (cls.width - 28) * time // 24
            draw_text(draw, (x, 160), Font.SMALL, f"{time:02}h", anchor="ma")

            draw_text(
                draw,
                (x, 178),
                Font.SMALL,
                f"{round(weather.hourly[time].temperature)}°",
                anchor="ma",
            )

            draw_icon(
                draw,
                (x - 8, 195),
                "small-" + weather.hourly[time].weather_code.value,
            )

            draw_text(
                draw,
                (x, 210),
                Font.SMALL,
                f"{round(weather.hourly[time].rain_probability)}%",
                anchor="ma",
            )
