import asyncio
import enum
import logging
from datetime import date, datetime, timedelta, time
from typing import ClassVar
from zoneinfo import ZoneInfo

import aiohttp
from icalevents.icalevents import events, Event
from pydantic import AnyHttpUrl, BaseModel, AwareDatetime, Field

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
    url: AnyHttpUrl = Field(description="public URL of the ICS calendar")
    label: str = Field(description="calendar name to display next to the events")


@enum.unique
class DayPeriod(enum.Enum):
    MORNING = 0
    NOON = 1
    AFTERNOON = 2
    EVENING = 3

    def time_span(self) -> tuple[time, time]:
        match self:
            case self.MORNING:
                return (time(0), time(11))
            case self.NOON:
                return (time(11), time(14))
            case self.AFTERNOON:
                return (time(14), time(18))
            case self.EVENING:
                return (time(18), time(23, 59))
            case _:
                raise NotImplementedError()

    def __lt__(self, other: "DayPeriod") -> bool:
        return self.value < other.value


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

    def is_full_day(self, day: date) -> bool:
        """
        Check if the event covers the whole given date.
        """
        return (
            self.date_start.date() <= day <= self.date_end.date()
            and self.date_start == self.date_end
        ) or (
            self.date_start
            <= datetime.combine(day, time(0, 0), tzinfo=self.date_start.tzinfo)
            and self.date_end
            >= datetime.combine(day, time(23, 59), tzinfo=self.date_end.tzinfo)
        )

    def day_period(self, day: date) -> DayPeriod:
        """
        Return the day period that best describes the event. If the event
        fully spans multiple periods, the earliest one is returned.
        """

        def period_ratio(period: DayPeriod) -> float:
            # Period bounds on day
            p_start = datetime.combine(
                day,
                period.time_span()[0],
                tzinfo=self.date_start.tzinfo,
            )

            p_end = datetime.combine(
                day,
                period.time_span()[1],
                tzinfo=self.date_end.tzinfo,
            )

            # Event bounds
            e_start = max(p_start, self.date_start)
            e_end = min(p_end, self.date_end)

            return (
                -(e_end - e_start).total_seconds() / (p_end - p_start).total_seconds()
            )

        period_ratios = [(period_ratio(period), period) for period in list(DayPeriod)]
        period_ratios.sort(key=lambda x: x[0])
        return period_ratios[0][1]


class ICSMetric(Metric):
    name: ClassVar[str] = "ics"
    all_events: list[ICSEvent]
    upcoming: list[ICSEvent]
    showcase: list[ICSEvent]

    def next_showcase_event(self, now: datetime) -> ICSEvent | None:
        return next(
            (event for event in self.showcase if event.date_end > now),
            None,
        )

    def on_date(self, day: date) -> list[ICSEvent]:
        return [
            event
            for event in self.all_events
            if (
                event.date_start.date() <= day
                and (
                    event.date_end
                    > datetime.combine(day, time(0, 0), tzinfo=event.date_end.tzinfo)
                )
            )
        ]


class ICSConfig(MetricConfig[ICSMetric], frozen=True):
    timezone: str = Field(description="your local timezone")
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
            all_events=all_events,
            upcoming=[event for event in all_events if now <= event.date_end],
            showcase=[event for event in all_events if Label.SHOWCASE in event.labels],
        )
