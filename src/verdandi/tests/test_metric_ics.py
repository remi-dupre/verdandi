import aiohttp
from datetime import datetime
from typing import AsyncGenerator
from zoneinfo import ZoneInfo

import pytest
from pydantic import AnyHttpUrl

from verdandi.metric.ics import ICSConfig, ICSMetric, ICSCalendar


@pytest.fixture
async def ics(http: aiohttp.ClientSession) -> AsyncGenerator[ICSMetric]:
    config = ICSConfig(
        timezone="Europe/Paris",
        calendars=(
            ICSCalendar(
                label="Holidays",
                url=AnyHttpUrl("https://calendar-url/french-holidays.ics"),
            ),
            ICSCalendar(
                label="Schedule",
                url=AnyHttpUrl("https://calendar-url/schedule.ics"),
            ),
        ),
    )

    yield await config.load(http)


def test_velib(ics: ICSMetric):
    tz = ZoneInfo("Europe/Paris")

    assert ics.upcoming[0].summary == "Coiffeur"
    assert ics.upcoming[0].date_start == datetime(2025, 11, 21, 12, 0, tzinfo=tz)
    assert ics.upcoming[0].date_end == datetime(2025, 11, 21, 13, 0, tzinfo=tz)
    assert ics.upcoming[0].calendar.label == "Schedule"

    for idx in range(1, 6):
        assert ics.upcoming[idx].summary == "Courses"

    assert ics.upcoming[6].summary == "Jour de Noël"
    assert ics.upcoming[6].date_start == datetime(2025, 12, 25, tzinfo=tz)
    assert ics.upcoming[6].date_end == datetime(2025, 12, 25, tzinfo=tz)
    assert ics.upcoming[6].calendar.label == "Holidays"

    assert ics.upcoming[7].summary == "Courses"

    assert ics.upcoming[8].summary == "1er janvier"
    assert ics.upcoming[8].date_start == datetime(2026, 1, 1, tzinfo=tz)
    assert ics.upcoming[8].date_end == datetime(2026, 1, 1, tzinfo=tz)
    assert ics.upcoming[8].calendar.label == "Holidays"
