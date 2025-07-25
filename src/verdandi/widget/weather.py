from datetime import datetime, timedelta

from PIL.ImageDraw import ImageDraw

from verdandi.widget.abs_widget import Widget
from verdandi.component.text import Font, draw_text
from verdandi.component.progress import draw_vertical_pill
from verdandi.component.icon import draw_icon
from verdandi.component.curve import draw_curve
from verdandi.metric.weather import WeatherMetric, WeatherConfig
from verdandi.util.date import weekday_humanized


MARGIN = 6


class WeatherRecap3x2(Widget):
    name = "weather-recap-3x2"
    width = 383
    height = 223

    weather: WeatherConfig

    @classmethod
    def example(cls) -> "WeatherRecap3x2":
        return WeatherRecap3x2(
            weather=WeatherConfig(
                lat=48.871,
                lon=2.292,
                timezone="Europe/Paris",
            )
        )

    def draw(self, draw: ImageDraw, weather: WeatherMetric):
        # Get biggest hour of the day that's before current time
        curr_date = weather.time.date()
        curr_time = weather.time.time()
        curr_time.replace(minute=0)
        curr_dt = datetime.combine(curr_date, curr_time)

        # Find temperature bounds
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

        draw_text(
            draw,
            (200, 18),
            Font.XMEDIUM_BOLD,
            f"{round(temp_min)}°-{round(temp_max)}°",
        )

        # Section: apparent temperature
        draw_text(draw, (200, 50), Font.SMALL, "Ressenti")

        draw_text(
            draw,
            (200, 58),
            Font.XMEDIUM_BOLD,
            f"{round(weather.temperature_apparent)}°",
        )

        # Section: sun events
        draw_text(draw, (290, 10), Font.SMALL, "Lever du Soleil")
        draw_text(draw, (290, 50), Font.SMALL, "Coucher du Soleil")

        draw_text(
            draw,
            (290, 18),
            Font.XMEDIUM_BOLD,
            weather.sunrise.isoformat("minutes"),
        )

        draw_text(
            draw,
            (290, 58),
            Font.XMEDIUM_BOLD,
            weather.sunset.isoformat("minutes"),
        )

        # Section: hourly
        def temp_func(val: float) -> float:
            hour = curr_time.hour + val * 24.0
            prev_val = weather.hourly[int(hour)].temperature

            if hour < 48.0:
                next_val = weather.hourly[int(hour) + 1].temperature
            else:
                next_val = prev_val

            alpha = hour % 1.0
            val = next_val * alpha + prev_val * (1.0 - alpha)
            return 0.1 + 0.9 * (val - temp_min) / (temp_max - temp_min)

        # Shade the curve between sunset & surise
        shade_day = 17
        shade_night = 5
        next_date = curr_date + timedelta(days=1)

        sun_events = [
            (datetime.combine(curr_date, weather.sunrise), shade_night),
            (datetime.combine(curr_date, weather.sunset), shade_day),
            (datetime.combine(next_date, weather.sunrise), shade_night),
            (datetime.combine(next_date, weather.sunset), shade_day),
        ]

        while curr_dt >= sun_events[0][0]:
            sun_events.pop(0)

        density = [
            ((dt - curr_dt).total_seconds() / (24.0 * 3600.0), density)
            for dt, density in sun_events[:2]
        ]

        density.append((1.0, shade_day + shade_night - density[-1][1]))
        draw_curve(draw, (14, 90, self.width - 14, 150), temp_func, density)

        for i in range(0, 25, 2):
            x = 14 + (self.width - 28) * i // 24
            hour = (curr_time.hour + i) % 24
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


class WeatherWeek3x1(Widget):
    name = "weather-week-3x1"
    width = 383
    height = 111

    weather: WeatherConfig

    @classmethod
    def example(cls) -> "WeatherWeek3x1":
        return WeatherWeek3x1(
            weather=WeatherConfig(
                lat=48.871,
                lon=2.292,
                timezone="Europe/Paris",
            )
        )

    def draw(self, draw: ImageDraw, weather: WeatherMetric):
        cell_width = 128
        cell_height = 50

        for i, day in enumerate(weather.daily[1:]):
            col = i % 3
            row = i // 3

            pos_x = MARGIN + col * cell_width
            pos_y = MARGIN + row * cell_height

            draw_icon(
                draw,
                (pos_x, pos_y),
                "large-" + day.weather_code.value,
            )

            draw_text(
                draw,
                (pos_x + 48, pos_y + 4),
                Font.MEDIUM,
                weekday_humanized(day.date).capitalize(),
            )

            draw_text(
                draw,
                (pos_x + 48, pos_y + 16),
                Font.XMEDIUM_BOLD,
                f"{round(day.temperature_min)}°-{round(day.temperature_max)}°",
            )

        draw.point([(x, MARGIN + 48) for x in range(21, self.width - 20, 3)])
