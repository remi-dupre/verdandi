from datetime import datetime, timedelta

from PIL.ImageDraw import ImageDraw

from verdandi.widget import Widget
from verdandi.component.text import Font, draw_text
from verdandi.component.pill import draw_vertical_pill
from verdandi.component.icon import draw_icon
from verdandi.component.curve import draw_curve
from verdandi.metric.weather import MetricWeather


MARGIN = 6


class WidgetWeather3x4(Widget):
    name = "weather-3x4"
    width = 383
    height = 223

    @classmethod
    def draw(cls, draw: ImageDraw, weather: MetricWeather):
        temp_min = min(min(x.temperature for x in weather.hourly), weather.temperature)
        temp_max = max(max(x.temperature for x in weather.hourly), weather.temperature)

        draw_icon(draw, (MARGIN, 22), "xlarge-" + weather.weather_code.value)
        draw_text(draw, (75, 10), Font.XLARGE, f"{round(weather.temperature)}°")

        # Section: min & max temperature
        draw_vertical_pill(
            draw,
            (190, 13, 196, 38),
            (weather.temperature - temp_min) / (temp_max - temp_min),
        )

        draw_text(draw, (200, 10), Font.SMALL, "Extrêmes")
        draw_text(draw, (200, 18), Font.LARGE, f"{round(temp_min)}°-{round(temp_max)}°")

        # Section: apparent temperature
        draw_text(draw, (200, 50), Font.SMALL, "Ressenti")

        draw_text(
            draw, (200, 58), Font.LARGE, f"{round(weather.temperature_apparent)}°"
        )

        # Section: sun events
        draw_text(draw, (295, 10), Font.SMALL, "Lever du Soleil")
        draw_text(draw, (295, 18), Font.LARGE, weather.sunrise.isoformat("minutes"))
        draw_text(draw, (295, 50), Font.SMALL, "Coucher du Soleil")
        draw_text(draw, (295, 58), Font.LARGE, weather.sunset.isoformat("minutes"))

        # Get biggest hour of the day that's before current time
        start_hour = weather.time.hour

        # Section: hourly
        def temp_func(val: float) -> float:
            hour = start_hour + val * 24.0
            prev_val = weather.hourly[int(hour)].temperature

            if hour < 48.0:
                next_val = weather.hourly[int(hour) + 1].temperature
            else:
                next_val = prev_val

            alpha = hour % 1.0
            val = next_val * alpha + prev_val * (1.0 - alpha)
            return 0.1 + 0.9 * (val - temp_min) / (temp_max - temp_min)

        # Shade the curve between sunset & surise
        curr_date = weather.time.date()
        curr_time = weather.time.time()

        if curr_time < weather.sunset:
            sunset = datetime.combine(curr_date, weather.sunset)
            sunset_cursor = (sunset - weather.time).total_seconds() / (24.0 * 3600.0)
            sunrise = datetime.combine(curr_date + timedelta(days=1), weather.sunrise)
            sunrise_cursor = (sunrise - weather.time).total_seconds() / (24.0 * 3600.0)
            density = [(sunset_cursor, 17), (sunrise_cursor, 5), (1.0, 17)]
        else:
            sunrise = datetime.combine(curr_date, weather.sunrise)
            sunrise_cursor = (sunrise - weather.time).total_seconds() / (24.0 * 3600.0)
            sunset = datetime.combine(curr_date + timedelta(days=1), weather.sunset)
            sunset_cursor = (sunset - weather.time).total_seconds() / (24.0 * 3600.0)
            density = [(sunrise_cursor, 5), (sunset_cursor, 17), (1.0, 5)]

        draw_curve(draw, (14, 90, cls.width - 14, 150), temp_func, density)

        for i in range(0, 25, 2):
            x = 14 + (cls.width - 28) * i // 24
            hour = (start_hour + i) % 24
            draw_text(draw, (x, 160), Font.SMALL, f"{hour:02}h", anchor="ma")

            draw_text(
                draw,
                (x, 178),
                Font.SMALL,
                f"{round(weather.hourly[hour].temperature)}°",
                anchor="ma",
            )

            draw_icon(
                draw,
                (x - 8, 195),
                "small-" + weather.hourly[hour].weather_code.value,
            )

            draw_text(
                draw,
                (x, 210),
                Font.SMALL,
                f"{round(weather.hourly[hour].rain_probability)}%",
                anchor="ma",
            )
