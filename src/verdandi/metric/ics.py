import asyncio
import enum
import logging
from datetime import date, datetime, timedelta
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


@enum.unique
class Label(enum.Enum):
    SHOWCASE = "showcase"
    IGNORE = "ignore"


class ICSCalendar(BaseModel, frozen=True):
    url: AnyHttpUrl
    label: str


class ICSEvent(BaseModel):
    summary: str
    calendar: ICSCalendar
    date_start: AwareDatetime
    date_end: AwareDatetime
    labels: set[Label]

    @classmethod
    def from_lib(
        cls,
        event: Event,
        calendar: ICSCalendar,
        tz: ZoneInfo,
    ) -> "ICSEvent":
        assert event.start is not None and event.end is not None  # TODO: when ???
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

        labels = {
            label
            for label in Label
            if f"verdandi:{label.value}" in (event.description or "").lower()
        }

        return cls(
            summary=event.summary or "",
            calendar=calendar,
            date_start=date_start,
            date_end=date_end,
            labels=labels,
        )


class ICSMetric(Metric):
    name: ClassVar[str] = "ics"
    upcoming: list[ICSEvent]
    showcase: list[ICSEvent]

    def next_showcase_event(self, now: datetime) -> ICSEvent | None:
        return next(
            (event for event in self.showcase if event.date_end > now),
            None,
        )


class ICSConfig(MetricConfig[ICSMetric], frozen=True):
    timezone: str
    calendars: tuple[ICSCalendar, ...]

    @staticmethod
    async def _load_from_url(
        http: aiohttp.ClientSession,
        cal: ICSCalendar,
        now: datetime,
    ) -> list[Event]:
        loop = asyncio.get_event_loop()

        async with http.get(str(cal.url)) as resp:
            data = await resp.read()

        events_res = await loop.run_in_executor(
            executor,
            lambda: events(
                string_content=data,
                start=datetime(now.year, 1, 1, tzinfo=now.tzinfo),
                end=now + timedelta(days=365),
                strict=True,
            ),
        )

        return events_res

    @async_time_cache(timedelta(hours=3))
    @async_log_duration(logger, "Loading all calendars")
    async def load(self, http: aiohttp.ClientSession) -> ICSMetric:
        tz = ZoneInfo(self.timezone)
        now = datetime.now(tz)

        parsed_calendars = await asyncio.gather(
            *(self._load_from_url(http, cal, now) for cal in self.calendars)
        )

        all_events = [
            event
            for calendar, lib_events in zip(self.calendars, parsed_calendars)
            for event in map(lambda e: ICSEvent.from_lib(e, calendar, tz), lib_events)
            if Label.IGNORE not in event.labels
        ]

        all_events.sort(key=lambda e: e.date_start)

        return ICSMetric(
            upcoming=[event for event in all_events if now <= event.date_end],
            showcase=[event for event in all_events if Label.SHOWCASE in event.labels],
        )
