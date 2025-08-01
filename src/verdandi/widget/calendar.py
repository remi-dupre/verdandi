from datetime import timedelta, date

from PIL.ImageDraw import ImageDraw

from verdandi.widget.abs_widget import Widget
from verdandi.util.draw import points_for_shade
from verdandi.util.date import weekday_humanized, month_humanized
from verdandi.metric.ics import ICSMetric, ICSConfig
from verdandi.component.text import Font, draw_text
from verdandi.util.text import keep_ascii

MARGIN = 3
MARGIN_DAY = 10


class Calendar3x4(Widget):
    name = "calendar-3x4"
    size = (3, 4)
    ics: ICSConfig

    @classmethod
    def example(cls) -> "Calendar3x4":
        return Calendar3x4(
            ics=ICSConfig(
                timezone="Europe/Paris",
                calendars=[],
            )
        )

    def draw(self, draw: ImageDraw, ics: ICSMetric):
        draw.point(
            points_for_shade(
                (MARGIN, MARGIN, MARGIN + 17, self.height - 2 * MARGIN),
                12,
            )
        )

        today = date.today()
        events_per_day = {}

        for event in ics.events:
            date_curr = event.date_start.date()
            date_end = event.date_end.date()

            while date_curr <= date_end:
                events_per_day.setdefault(date_curr, []).append(event)
                date_curr += timedelta(days=1)

        y_pos = MARGIN
        prev_day = None

        for day, events in events_per_day.items():
            if y_pos > self.height - (24 + MARGIN_DAY):
                break

            if day == today:
                text = "AUJOURD'HUI"
            elif day + timedelta(days=1) == today:
                text = "DEMAIN"
            elif day - today < timedelta(days=7):
                text = weekday_humanized(day).upper()
            elif prev_day is None or day.month != prev_day.month:
                text = month_humanized(day).upper()
            else:
                text = None

            draw_text(
                draw,
                (MARGIN + 9, y_pos + 4),
                Font.MEDIUM,
                str(day.day),
                anchor="ma",
            )

            if text is not None:
                draw_text(draw, (28, y_pos), Font.XMEDIUM_BOLD, text)
                y_pos += 24

            for event in events:
                if y_pos > self.height - 24:
                    break

                time_str = (
                    event.date_start.strftime("%Hh%M")
                    + "-"
                    + event.date_end.strftime("%Hh%M")
                ).replace("h00", "h")

                if time_str == "00h-00h":
                    draw_text(
                        draw,
                        (28, y_pos),
                        Font.XMEDIUM,
                        keep_ascii(event.summary),
                    )
                else:
                    draw_text(draw, (73, y_pos + 9), Font.MEDIUM, time_str, anchor="mt")

                    draw.rounded_rectangle(
                        (28, y_pos + 5, 28 + 89, y_pos + 21), radius=3
                    )

                    draw_text(
                        draw,
                        (122, y_pos),
                        Font.XMEDIUM,
                        keep_ascii(event.summary),
                    )
                y_pos += 24

            y_pos += MARGIN_DAY
            prev_day = day
