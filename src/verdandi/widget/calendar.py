from datetime import timedelta, date, datetime, time

from PIL.ImageDraw import ImageDraw

from verdandi.widget.abs_widget import Widget
from verdandi.util.draw import points_for_shade
from verdandi.util.date import weekday_humanized, month_humanized
from verdandi.metric.ics import ICSMetric, ICSConfig
from verdandi.component.text import Font, draw_text, TextArea, size_text
from verdandi.component.icon import draw_icon
from verdandi.util.text import keep_ascii, guess_icon

MARGIN = 3
MARGIN_LINES = 4
MARGIN_DAY = 8


class Calendar3x4(Widget):
    name = "calendar-3x4"
    size = (3, 4)
    ics: ICSConfig

    @classmethod
    def example(cls) -> "Calendar3x4":
        return Calendar3x4(
            ics=ICSConfig(
                timezone="Europe/Paris",
                calendars=tuple(),
            )
        )

    def draw(self, draw: ImageDraw, ics: ICSMetric):
        draw.point(
            points_for_shade(
                (MARGIN, MARGIN, MARGIN + 17, self.height() - 2 * MARGIN),
                12,
            )
        )

        today = date.today()
        events_per_day = {}

        for event in ics.upcoming:
            date_curr = event.date_start.date()
            date_end = (event.date_end - timedelta(seconds=1)).date()

            while date_curr <= date_end:
                events_per_day.setdefault(date_curr, []).append(event)
                date_curr += timedelta(days=1)

        y_pos = MARGIN
        prev_day = None

        for day, events in iter(events_per_day.items()):
            if y_pos > self.height() - (24 + MARGIN_DAY):
                break

            if day == today:
                text = "AUJOURD'HUI"
            elif day == today + timedelta(days=1):
                text = "DEMAIN"
            elif day - today < timedelta(days=7):
                text = weekday_humanized(day).upper()
            elif prev_day is None or day.month != prev_day.month:
                text = month_humanized(day).upper()
            else:
                text = None

            if text is not None:
                draw_text(draw, (28, y_pos), Font.XMEDIUM_BOLD, text)
                title_width = size_text(draw, Font.XMEDIUM_BOLD, text) + 10
                y_pos += 12
            else:
                title_width = 0

            draw_text(
                draw,
                (MARGIN + 9, y_pos),
                Font.MEDIUM,
                str(day.day),
                anchor="mm",
            )

            draw.point(
                [(x, y_pos) for x in range(28 + title_width, self.width() - MARGIN, 2)]
            )

            y_pos += 12

            for event in events:
                if y_pos > self.height() - 24:
                    break

                time_start = max(
                    event.date_start,
                    datetime.combine(
                        day,
                        time(0, 0),
                        tzinfo=event.date_start.tzinfo,
                    ),
                )

                time_end = min(
                    event.date_end,
                    datetime.combine(
                        day + timedelta(days=1),
                        time(0, 0),
                        tzinfo=event.date_end.tzinfo,
                    ),
                )

                time_str = (
                    time_start.strftime("%Hh%M") + "-" + time_end.strftime("%Hh%M")
                ).replace("h00", "h")

                # Initial position for the text area
                initial_cursor_x = 0

                if time_str != "00h-00h":
                    initial_cursor_x += 94
                    draw_text(draw, (73, y_pos + 7), Font.MEDIUM, time_str, anchor="mt")

                    draw.rounded_rectangle(
                        (28, y_pos + 3, 28 + 89, y_pos + 19), radius=3
                    )

                if icon := guess_icon(event.summary):
                    draw_icon(draw, (28 + initial_cursor_x, y_pos + 3), "small-" + icon)
                    initial_cursor_x += 18

                text_area = TextArea(
                    draw=draw,
                    bounds=(28, y_pos, self.width() - MARGIN, None),
                    line_height=22,
                    cursor=(initial_cursor_x, 0),
                )

                text_area.draw_text(Font.XMEDIUM, keep_ascii(event.summary))

                text_area.draw_text(
                    Font.MEDIUM,
                    f"- {event.calendar.label}",
                    breakable=False,
                )

                y_pos += text_area.height + MARGIN_LINES

            y_pos += MARGIN_DAY
            prev_day = day
