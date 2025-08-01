import asyncio
import logging
from datetime import date, datetime, timedelta
from functools import cache
from typing import ClassVar
from zoneinfo import ZoneInfo

import aiohttp
import icalendar
from pydantic import AnyHttpUrl, BaseModel, AwareDatetime

from verdandi.metric.abs_metric import Metric, MetricConfig
from verdandi.util.cache import async_time_cache
from verdandi.util.logging import async_log_duration
from verdandi.util.common import executor

logger = logging.getLogger(__name__)


class ICSCalendar(BaseModel):
    url: AnyHttpUrl
    label: str


class ICSEvent(BaseModel):
    summary: str
    calendar: ICSCalendar
    date_start: AwareDatetime
    date_end: AwareDatetime

    @classmethod
    def from_lib(
        cls,
        event: icalendar.Event,
        calendar: ICSCalendar,
        tz: ZoneInfo,
    ) -> "ICSEvent":
        date_start = event.DTSTART
        date_end = event.DTEND

        if type(date_start) is date:
            date_start = datetime.combine(date_start, datetime.min.time())

        if type(date_end) is date:
            date_end = datetime.combine(date_end, datetime.min.time())

        if date_start.tzinfo is None:
            date_start = date_start.replace(tzinfo=tz)

        if date_end.tzinfo is None:
            date_end = date_end.replace(tzinfo=tz)

        date_start = date_start.astimezone(tz)
        date_end = date_end.astimezone(tz)

        return cls(
            summary=event.get("SUMMARY", "???"),
            calendar=calendar,
            date_start=date_start,
            date_end=date_end,
        )


class ICSMetric(Metric):
    name: ClassVar[str] = "ics"
    events: list[ICSEvent]


class ICSConfig(MetricConfig[ICSMetric]):
    name: str = "ics"
    timezone: str
    calendars: list[ICSCalendar]

    @staticmethod
    @cache
    def get_http_client() -> aiohttp.ClientSession:
        # TODO: why? is this a NixOS issue?
        connector = aiohttp.TCPConnector(ssl=False)
        return aiohttp.ClientSession(connector=connector)

    @classmethod
    async def _load_from_url(cls, cal: ICSCalendar) -> icalendar.Calendar:
        loop = asyncio.get_event_loop()

        async with cls.get_http_client().get(str(cal.url)) as resp:
            data = await resp.read()

        return await loop.run_in_executor(
            executor,
            lambda: icalendar.Calendar.from_ical(data),
        )

    @async_time_cache(timedelta(hours=3))
    @async_log_duration(logger, "Loading all calendars")
    async def load(self) -> ICSMetric:
        tz = ZoneInfo(self.timezone)
        now = datetime.now(tz)
        events = []

        parsed_calendars = await asyncio.gather(
            *(self._load_from_url(cal) for cal in self.calendars)
        )

        for calendar, parsed_calendar in zip(self.calendars, parsed_calendars):
            events += [
                event
                for event in map(
                    lambda e: ICSEvent.from_lib(e, calendar, tz),
                    parsed_calendar.events,
                )
                if now <= event.date_end
            ]

        events.sort(key=lambda e: e.date_start)
        return ICSMetric(events=events)
