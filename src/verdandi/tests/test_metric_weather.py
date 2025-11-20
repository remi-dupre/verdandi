from datetime import datetime

import aiohttp
import pytest
from typing import AsyncGenerator

from verdandi.metric.weather import WeatherConfig, WeatherMetric


@pytest.fixture
async def weather(http: aiohttp.ClientSession) -> AsyncGenerator[WeatherMetric]:
    config = WeatherConfig(lat=48.86, lon=2.34, timezone="Europe/Paris")
    yield await config.load(http)


def test_weather_parsing(weather: WeatherMetric):
    assert weather.temperature == 12.6
    assert weather.temperature_apparent == 12.0


def test_weather_interpolate(weather: WeatherMetric):
    assert (
        weather.interpolate_temperature_at(datetime.fromisoformat("2025-11-15T00:00"))
        == 15.2
    )

    assert (
        weather.interpolate_temperature_at(datetime.fromisoformat("2025-11-15T01:00"))
        == 15.0
    )

    assert (
        weather.interpolate_temperature_at(datetime.fromisoformat("2025-11-15T01:15"))
        == 14.9
    )

    assert (
        weather.interpolate_temperature_at(datetime.fromisoformat("2025-11-15T01:45"))
        == 14.7
    )

    assert (
        weather.interpolate_temperature_at(datetime.fromisoformat("2025-11-15T02:00"))
        == 14.6
    )


def test_weather_interpolate_oob(weather: WeatherMetric):
    assert (
        weather.interpolate_temperature_at(datetime.fromisoformat("2025-08-15T12:00"))
        == 15.2
    )

    assert (
        weather.interpolate_temperature_at(datetime.fromisoformat("2026-01-15T12:00"))
        == 2.3
    )
