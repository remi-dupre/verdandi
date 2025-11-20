import aiohttp
import pytest
from typing import AsyncGenerator

from verdandi.metric.velib import VelibConfig, VelibMetric


@pytest.fixture
async def velib(http: aiohttp.ClientSession) -> AsyncGenerator[VelibMetric]:
    yield await VelibConfig(station_id=213686196).load(http)


def test_velib(velib: VelibMetric):
    assert velib.station_name == "Lauriston - Copernic"
    assert velib.mechanical == 1
    assert velib.electric == 2
    assert velib.parking == 16
    assert velib.capacity == 19
