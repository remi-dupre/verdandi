import aiohttp
from verdandi.metric.weather import WeatherConfig


async def test_weather(http: aiohttp.ClientSession):
    config = WeatherConfig(lat=48.86, lon=2.34, timezone="Europe/Paris")
    weather = await config.load(http)
    assert weather.temperature == 12.6
    assert weather.temperature_apparent == 12.0
