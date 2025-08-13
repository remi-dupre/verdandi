import asyncio
import logging
from datetime import date, datetime, timedelta
from functools import cache
from typing import ClassVar
from zoneinfo import ZoneInfo

import aiohttp
from icalevents.icalevents import events, Event
from pydantic import AnyHttpUrl, BaseModel, AwareDatetime

from verdandi.metric.abs_metric import Metric, MetricConfig
from verdandi.util.cache import async_time_cache
from verdandi.util.logging import async_log_duration
from verdandi.util.common import executor

logger = logging.getLogger(__name__)


class ICSCalendar(BaseModel, frozen=True):
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
        event: Event,
        calendar: ICSCalendar,
        tz: ZoneInfo,
    ) -> "ICSEvent":
        date_start = event.start
        date_end = event.end

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
            summary=event.summary,
            calendar=calendar,
            date_start=date_start,
            date_end=date_end,
        )


class ICSMetric(Metric):
    name: ClassVar[str] = "ics"
    events: list[ICSEvent]


class ICSConfig(MetricConfig[ICSMetric], frozen=True):
    name: str = "ics"
    timezone: str
    calendars: tuple[ICSCalendar, ...]

    @staticmethod
    @cache
    def get_http_client() -> aiohttp.ClientSession:
        # TODO: why? is this a NixOS issue?
        connector = aiohttp.TCPConnector(ssl=False)
        return aiohttp.ClientSession(connector=connector)

    @classmethod
    async def _load_from_url(cls, cal: ICSCalendar) -> list[Event]:
        loop = asyncio.get_event_loop()

        async with cls.get_http_client().get(str(cal.url)) as resp:
            data = await resp.read()

        events_res = await loop.run_in_executor(
            executor,
            lambda: events(
                string_content=data,
                start=datetime.now(),
                end=datetime.now() + timedelta(days=365),
                strict=True,
            ),
        )

        return events_res

    @async_time_cache(timedelta(hours=3))
    @async_log_duration(logger, "Loading all calendars")
    async def load(self) -> ICSMetric:
        tz = ZoneInfo(self.timezone)
        now = datetime.now(tz)
        events = []

        parsed_calendars = await asyncio.gather(
            *(self._load_from_url(cal) for cal in self.calendars)
        )

        for calendar, lib_events in zip(self.calendars, parsed_calendars):
            events += [
                event
                for event in map(
                    lambda e: ICSEvent.from_lib(e, calendar, tz),
                    lib_events,
                )
                if now <= event.date_end
            ]

        events.sort(key=lambda e: e.date_start)
        return ICSMetric(events=events)
