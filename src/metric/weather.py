from datetime import datetime, time
from dataclasses import dataclass
from enum import Enum


class WeatherCode(Enum):
    CLEAR = "clear"
    MAINLY_CLEAR = "mainly-clear"
    PARTLY_CLOUDY = "partly-cloudy"
    OVERCAST = "overcast"
    FOG = "fog"
    RAIN_LIGHT = "rain-light"
    RAIN_MODERATE = "rain-moderate"
    RAIN_HEAVY = "rain-heavy"
    SNOW_FALL_LIGHT = "snow-fall-light"
    SNOW_FALL_MODERATE = "snow-fall-moderate"
    SNOW_FALL_HEAVY = "snow-fall-heavy"
    THUNDER = "thunder"


@dataclass
class WeatherPoint:
    temperature: float
    weather_code: WeatherCode
    rain_probability: float


@dataclass
class MetricWeather:
    time: datetime
    temperature: float
    temperature_apparent: float
    weather_code: WeatherCode
    sunrise: time
    sunset: time
    hourly: list[WeatherPoint]
