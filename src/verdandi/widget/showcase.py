import logging
from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic import AnyHttpUrl
from PIL.ImageDraw import ImageDraw

from verdandi.component.icon import draw_icon
from verdandi.component.progress import draw_progress
from verdandi.component.text import Font, draw_text
from verdandi.metric.ics import ICSConfig, ICSMetric, ICSCalendar
from verdandi.util.text import summary_to_category, keep_ascii
from verdandi.widget.abs_widget import Widget
from verdandi.util.draw import ShadeMatrix
from verdandi.util.color import CW, CL

MARGIN = 10
MARGIN_LINES = 4
MARGIN_DAY = 8

logger = logging.getLogger(__name__)


SHADE_PROGRESS = ShadeMatrix(
    [CL, CW],
    [CW, CL],
)


class Showcase2x1(Widget):
    name = "showcase-2x1"
    size = (2, 1)
    ics: ICSConfig

    @classmethod
    def example(cls) -> "Showcase2x1":
        return Showcase2x1(
            ics=ICSConfig(
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
        )

    def draw(self, draw: ImageDraw, ics: ICSMetric):
        tz = ZoneInfo(self.ics.timezone)
        now = datetime.now(tz)
        year_start = date(now.year, 1, 1)
        year_end = date(now.year + 1, 1, 1)

        # == Display progress bar
        progress = min(
            1.0,
            (now.date() - year_start) / (year_end - year_start),
        )

        bar_x_start = 20
        bar_x_end = self.width() - 20

        draw_progress(
            draw,
            (bar_x_start, 79, bar_x_end, 95),
            progress,
            fill=SHADE_PROGRESS,
        )

        for i, month in enumerate("JFMAMJJASOND"):
            text_x = bar_x_start + i * (bar_x_end - bar_x_start) // 12
            draw_text(draw, (text_x, 100), Font.SMALL, month, anchor="ma")

        # == Display markers
        for event in ics.showcase:
            if event.date_start.year != now.year:
                continue

            year_progress = (event.date_start.date() - year_start) / (
                year_end - year_start
            )

            icon = summary_to_category(event.summary) or "unknown"
            icon_x = bar_x_start + int(year_progress * (bar_x_end - bar_x_start))
            draw_icon(draw, (icon_x - 8, 60), "small-" + icon)

        # == Display next event
        event = ics.next_showcase_event(now)

        if event is None:
            logger.warning("No showcase event was found")
            return

        remaining = (event.date_start - now).days + 1
        text = f"Dans {remaining} jours"
        title_x = MARGIN

        if icon := summary_to_category(event.summary):
            draw_icon(draw, (title_x, 9), "small-" + icon)
            title_x += 18

        draw_text(draw, (title_x, 1), Font.LARGE_BOLD, keep_ascii(event.summary))
        draw_text(draw, (MARGIN, 25), Font.LARGE, text)
