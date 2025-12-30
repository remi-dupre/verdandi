from datetime import datetime, timedelta

from PIL.ImageDraw import ImageDraw

from verdandi.component.curve import draw_curve
from verdandi.component.icon import draw_icon
from verdandi.component.progress import draw_vertical_pill
from verdandi.component.text import Font, draw_text
from verdandi.metric.weather import WeatherConfig, WeatherMetric
from verdandi.util.color import CB, CD, CL, CW
from verdandi.util.date import next_time_cadenced, weekday_humanized
from verdandi.util.draw import ShadeMatrix
from verdandi.widget.abs_widget import Widget

MARGIN = 6
MIN_CURVE_RANGE = 6.0

# Display a different sunny icon when it's cold
EASTER_EGG_COLD_SUN_THRESHOLD = 8  # °C


FILL_DAY = ShadeMatrix(
    [CW, CW, CL, CW],
    [CW, CW, CW, CW],
    [CL, CW, CW, CW],
    [CW, CW, CW, CW],
)

FILL_NIGHT = ShadeMatrix(
    [CD, CW, CL, CW],
    [CW, CW, CW, CW],
    [CL, CW, CD, CW],
    [CW, CW, CW, CW],
)

# Dashed lanes on the curve are represented with a matrix with same column
# alignment as fills which allows to control which part of the pattern may
# be overriden or not.
DASHED_LINE = [CW] * 4 + [CB] * 3 + [CW] * 2
DASHED_SCALE = ShadeMatrix(DASHED_LINE, [CW], DASHED_LINE, [CW])


class WeatherRecap3x2(Widget):
    name = "weather-recap-3x2"
    size = (3, 2)
    weather: WeatherConfig

    def next_update(self, now: datetime) -> datetime:
        return next_time_cadenced(now, timedelta(hours=1))

    @classmethod
    def example(cls) -> "WeatherRecap3x2":
        return WeatherRecap3x2(
            weather=WeatherConfig(
                lat=48.871,
                lon=2.292,
                timezone="Europe/Paris",
            )
        )

    def draw(self, draw: ImageDraw, weather: WeatherMetric):  # ty: ignore[invalid-method-override]
        # Get biggest hour of the day that's before current time
        curr_date = weather.time.date()
        curr_time = weather.time.time()
        curr_time.replace(minute=0)
        curr_dt = datetime.combine(curr_date, curr_time)

        # Extract temperature bounds for today
        today_temp_min = weather.daily[0].temperature_min
        today_temp_max = weather.daily[0].temperature_max

        # Section: temperature and weather now
        xlarge_icon = "xlarge-" + weather.weather_code.value

        if (
            xlarge_icon == "xlarge-clear"
            and weather.temperature < EASTER_EGG_COLD_SUN_THRESHOLD
        ):
            xlarge_icon += "-cold"

        draw_icon(draw, (MARGIN, 22), xlarge_icon)
        draw_text(draw, (75, 10), Font.XLARGE, f"{round(weather.temperature)}°")

        # Section: min & max temperature
        draw_vertical_pill(
            draw,
            (190, 13, 196, 38),
            (weather.temperature - today_temp_min) / (today_temp_max - today_temp_min),
        )

        draw_text(draw, (200, 10), Font.SMALL, "Extrêmes")

        draw_text(
            draw,
            (200, 18),
            Font.XMEDIUM_BOLD,
            f"{round(today_temp_min)}°|{round(today_temp_max)}°",
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

        # == Draw curve

        # Find temperature bounds for the next two days
        temp_min, temp_max = weather.temerature_bounds(
            curr_dt,
            curr_dt + timedelta(hours=24.0),
        )

        displayed_min = 0.0 if temp_min > 0.0 else temp_min
        displayed_max = 0.0 if temp_max < 0.0 else temp_max

        if displayed_max - displayed_min < MIN_CURVE_RANGE:
            missing_space = MIN_CURVE_RANGE - displayed_max + displayed_min
            displayed_min -= missing_space / 2
            displayed_max += missing_space / 2

        scale_precision = 5 if displayed_max - displayed_min < 20 else 10

        def temp_y_coord(temp: float) -> float:
            return (temp - displayed_min) / (displayed_max - displayed_min)

        displayed_scale = [
            (f"{temp}°", temp_y_coord(temp), DASHED_SCALE)
            for temp in range(int(displayed_min), int(displayed_max) + 1)
            if temp % scale_precision == 0
        ]

        # Section: hourly
        def temp_func(x: float) -> float:
            dt = curr_dt + timedelta(hours=24.0 * x)
            temp = weather.interpolate_temperature_at(dt)
            return temp_y_coord(temp)

        # Shade the curve between sunset & surise
        next_date = curr_date + timedelta(days=1)

        sun_events = [
            (datetime.combine(curr_date, weather.sunrise), FILL_NIGHT),
            (datetime.combine(curr_date, weather.sunset), FILL_DAY),
            (datetime.combine(next_date, weather.sunrise), FILL_NIGHT),
            (datetime.combine(next_date, weather.sunset), FILL_DAY),
        ]

        while curr_dt >= sun_events[0][0]:
            sun_events.pop(0)

        shade_parts = [
            ((dt - curr_dt).total_seconds() / (24.0 * 3600.0), shade)
            for dt, shade in sun_events[:2]
        ]

        shade_parts.append(
            (
                1.0,
                FILL_DAY if shade_parts[-1][1] == FILL_NIGHT else FILL_NIGHT,
            )
        )

        curve_x_pos = 20

        draw_curve(
            draw,
            (curve_x_pos, 90, self.width() - curve_x_pos, 150),
            temp_func,
            shade_parts,
            y_scale=displayed_scale,
            y_origin=temp_y_coord(0.0),
        )

        # == Draw Table

        # First hour in table representation
        first_hour = curr_time.hour if curr_time.minute < 30 else curr_time.hour + 1

        # Offset induced by current minutes
        minutes_offset = (
            (self.width() - curve_x_pos - 14) * curr_time.minute // (24 * 60)
        )

        # If minutes induce no offset, then there is room to display an extra column
        displayed_range = 25 if minutes_offset == 0 else 24

        for i in range(0, displayed_range, 2):
            hour = first_hour + i

            x = (
                curve_x_pos
                + minutes_offset
                + (self.width() - curve_x_pos - 14) * i // 24
            )

            draw_text(draw, (x, 160), Font.SMALL, f"{(hour % 24):02}h", anchor="ma")

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
    size = (3, 1)
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

    def draw(self, draw: ImageDraw, weather: WeatherMetric):  # ty:ignore[invalid-method-override]
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
                f"{round(day.temperature_min)}°|{round(day.temperature_max)}°",
            )

        draw.point([(x, MARGIN + 48) for x in range(21, self.width() - 20, 3)])
