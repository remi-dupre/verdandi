import logging
from datetime import datetime, time, date, timedelta
from enum import Enum
from functools import cache
from typing import ClassVar

import aiohttp
from pydantic import BaseModel, conlist

from verdandi.metric.abs_metric import Metric, MetricConfig
from verdandi.util.logging import async_log_duration
from verdandi.util.cache import async_time_cache


logger = logging.getLogger(__name__)


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

    @classmethod
    def from_wmo_mapping(cls, wmo_code: int) -> "WeatherCode":
        return cls.wmo_mapping().get(wmo_code, cls.UNKNOWN)

    @classmethod
    @cache
    def wmo_mapping(cls) -> dict[int, "WeatherCode"]:
        rev_mapping = {
            cls.CLEAR: [0],
            cls.MAINLY_CLEAR: [1],
            cls.PARTLY_CLOUDY: [2],
            cls.OVERCAST: [3],
            cls.FOG: [45, 48],
            cls.RAIN_LIGHT: [51, 53, 55, 56, 57, 61, 66, 80],
            cls.RAIN_MODERATE: [63, 81],
            cls.RAIN_HEAVY: [65, 67, 82],
            cls.SNOW_FALL_LIGHT: [71],
            cls.SNOW_FALL_MODERATE: [73, 77],
            cls.SNOW_FALL_HEAVY: [75],
            cls.THUNDER: [95, 96, 99],
        }

        return {
            num: code for (code, num_list) in rev_mapping.items() for num in num_list
        }


class HourlyData(BaseModel):
    temperature: float
    weather_code: WeatherCode
    rain_probability: float


class DailyData(BaseModel):
    date: date
    weather_code: WeatherCode
    temperature_min: float
    temperature_max: float


class WeatherMetric(Metric):
    name = "weather"
    time: datetime
    temperature: float
    temperature_apparent: float
    weather_code: WeatherCode
    sunrise: time
    sunset: time
    daily: list[DailyData] = conlist(DailyData, min_length=7, max_length=7)
    hourly: list[HourlyData] = conlist(HourlyData, min_length=49, max_length=49)


class WeatherConfig(MetricConfig[WeatherMetric], frozen=True):
    lat: float
    lon: float
    timezone: str

    API_URL: ClassVar[str] = "https://api.open-meteo.com/v1/forecast"

    API_DAILY_METRICS: ClassVar[list[str]] = [
        "sunrise",
        "sunset",
        "weather_code",
        "temperature_2m_min",
        "temperature_2m_max",
    ]

    API_HOURLY_METRICS: ClassVar[list[str]] = [
        "temperature_2m",
        "weather_code",
        "precipitation_probability",
    ]

    API_CURRENT_METRICS: ClassVar[list[str]] = [
        "temperature_2m",
        "apparent_temperature",
        "weather_code",
    ]

    @staticmethod
    @cache
    def get_http_client() -> aiohttp.ClientSession:
        # TODO: why? is this a NixOS issue?
        connector = aiohttp.TCPConnector(ssl=False)
        return aiohttp.ClientSession(connector=connector)

    @async_time_cache(timedelta(minutes=5))
    @async_log_duration(logger, "Fetch weather data")
    async def load(self) -> WeatherMetric:
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "daily": ",".join(self.API_DAILY_METRICS),
            "hourly": ",".join(self.API_HOURLY_METRICS),
            "current": ",".join(self.API_CURRENT_METRICS),
            "timezone": self.timezone,
        }

        async with self.get_http_client().get(self.API_URL, params=params) as resp:
            data = await resp.json()

        daily = [
            DailyData(
                date=date.fromisoformat(time_str),
                weather_code=WeatherCode.from_wmo_mapping(wmo_code),
                temperature_min=temperature_min,
                temperature_max=temperature_max,
            )
            for (time_str, wmo_code, temperature_min, temperature_max) in zip(
                data["daily"]["time"],
                data["daily"]["weather_code"],
                data["daily"]["temperature_2m_min"],
                data["daily"]["temperature_2m_max"],
            )
        ]

        hourly = [
            HourlyData(
                temperature=temperature,
                weather_code=WeatherCode.from_wmo_mapping(wmo_code),
                rain_probability=rain_probability,
            )
            for (temperature, wmo_code, rain_probability) in zip(
                data["hourly"]["temperature_2m"],
                data["hourly"]["weather_code"],
                data["hourly"]["precipitation_probability"],
            )
        ]

        return WeatherMetric(
            time=datetime.fromisoformat(data["current"]["time"]),
            temperature=data["current"]["temperature_2m"],
            temperature_apparent=data["current"]["apparent_temperature"],
            weather_code=WeatherCode.from_wmo_mapping(data["current"]["weather_code"]),
            sunrise=datetime.fromisoformat(data["daily"]["sunrise"][0]).time(),
            sunset=datetime.fromisoformat(data["daily"]["sunset"][0]).time(),
            daily=daily,
            hourly=hourly,
        )
