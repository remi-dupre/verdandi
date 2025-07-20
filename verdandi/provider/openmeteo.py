from datetime import datetime

import aiohttp

from verdandi.metric.weather import WeatherCode, MetricWeather, WeatherPoint

WMO_REV_MAPPING = {
    WeatherCode.CLEAR: [0],
    WeatherCode.MAINLY_CLEAR: [1],
    WeatherCode.PARTLY_CLOUDY: [2],
    WeatherCode.OVERCAST: [3],
    WeatherCode.FOG: [45, 48],
    WeatherCode.RAIN_LIGHT: [51, 53, 55, 56, 57, 61, 66, 80],
    WeatherCode.RAIN_MODERATE: [63, 81],
    WeatherCode.RAIN_HEAVY: [65, 67, 82],
    WeatherCode.SNOW_FALL_LIGHT: [71],
    WeatherCode.SNOW_FALL_MODERATE: [73, 77],
    WeatherCode.SNOW_FALL_HEAVY: [75],
    WeatherCode.THUNDER: [95, 96, 99],
}

WMO_MAPPING = {
    num: code for (code, num_list) in WMO_REV_MAPPING.items() for num in num_list
}


async def get_weather() -> MetricWeather:
    url = "https://api.open-meteo.com/v1/forecast?latitude=48.8534&longitude=2.3488&daily=sunrise,sunset&hourly=temperature_2m,weather_code,precipitation_probability&current=temperature_2m,apparent_temperature,weather_code&timezone=Europe/Paris"

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(verify_ssl=False)
    ) as http:
        async with http.get(url) as resp:
            data = await resp.json()

    hourly = [
        WeatherPoint(
            temperature=data["hourly"]["temperature_2m"][i],
            weather_code=WMO_MAPPING.get(
                data["hourly"]["weather_code"][i],
                WeatherCode.UNKNOWN,
            ),
            rain_probability=data["hourly"]["precipitation_probability"][i],
        )
        for i in range(0, 25)
    ]

    return MetricWeather(
        time=datetime.fromisoformat(data["current"]["time"]),
        temperature=data["current"]["temperature_2m"],
        temperature_apparent=data["current"]["apparent_temperature"],
        weather_code=WMO_MAPPING.get(
            data["current"]["weather_code"],
            WeatherCode.UNKNOWN,
        ),
        sunrise=datetime.fromisoformat(data["daily"]["sunrise"][0]).time(),
        sunset=datetime.fromisoformat(data["daily"]["sunset"][0]).time(),
        hourly=hourly,
    )
