import logging
import asyncio
from functools import cache
from typing import ClassVar
from datetime import timedelta

import aiohttp

from verdandi.metric.abs_metric import Metric, MetricConfig
from verdandi.util.logging import async_log_duration
from verdandi.util.cache import async_time_cache


logger = logging.getLogger(__name__)


class VelibMetric(Metric):
    name = "velib"
    station_name: str
    mechanical: int
    electric: int
    parking: int
    capacity: int


class VelibConfig(MetricConfig[VelibMetric]):
    API_URL: ClassVar[str] = (
        "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole"
    )

    station_id: int

    @classmethod
    @async_time_cache(timedelta(hours=1))
    @async_log_duration(logger, "Fetch velib informations")
    async def get_stations_information(cls, http: aiohttp.ClientSession) -> dict:
        url = cls.API_URL + "/station_information.json"

        async with http.get(url) as resp:
            data = await resp.json()

        return data["data"]["stations"]

    @classmethod
    @async_time_cache(timedelta(seconds=30))
    @async_log_duration(logger, "Fetch velib statuses")
    async def get_stations_status(cls, http: aiohttp.ClientSession) -> dict:
        url = cls.API_URL + "/station_status.json"

        async with http.get(url) as resp:
            data = await resp.json()

        return data["data"]["stations"]

    async def load(self, http: aiohttp.ClientSession) -> VelibMetric:
        list_stations, list_status = await asyncio.gather(
            self.get_stations_information(http),
            self.get_stations_status(http),
        )

        status = next(
            status for status in list_status if status["station_id"] == self.station_id
        )

        station = next(
            station
            for station in list_stations
            if station["station_id"] == self.station_id
        )

        mechanical = 0
        electric = 0

        for item in status["num_bikes_available_types"]:
            for kind, count in item.items():
                match kind:
                    case "mechanical":
                        mechanical = count
                    case "ebike":
                        electric = count
                    case _:
                        logger.warning(
                            "Unknown bike kind %s: %d available", kind, count
                        )

        return VelibMetric(
            station_name=station["name"],
            mechanical=mechanical,
            electric=electric,
            parking=status["num_docks_available"],
            capacity=station["capacity"],
        )
