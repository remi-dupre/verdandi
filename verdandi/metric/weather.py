from datetime import datetime, time
from enum import Enum

from pydantic import BaseModel, conlist


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
    UNKNOWN = "unknown"


class WeatherPoint(BaseModel):
    temperature: float
    weather_code: WeatherCode
    rain_probability: float


class MetricWeather(BaseModel):
    time: datetime
    temperature: float
    temperature_apparent: float
    weather_code: WeatherCode
    sunrise: time
    sunset: time
    hourly: list[WeatherPoint] = conlist(WeatherPoint, min_length=49, max_length=49)
