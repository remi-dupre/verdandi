from datetime import date, timedelta

from PIL.ImageDraw import ImageDraw
from pydantic import AnyHttpUrl

from verdandi.component.text import Font, draw_text
from verdandi.metric.ics import ICSCalendar, ICSConfig, ICSMetric
from verdandi.util.color import CB, CD, CL, CW
from verdandi.util.text import summary_to_category
from verdandi.widget.abs_widget import Widget

MARGIN = 7
CELL_SPACING = 2
CELL_HEIGHT = 18
CELL_WIDTH = 15


class Calendar1x1(Widget):
    name = "calendar-1x1"
    size = (1, 1)
    ics: ICSConfig

    @classmethod
    def example(cls) -> "Calendar1x1":
        return Calendar1x1(
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

    def draw(self, draw: ImageDraw, ics: ICSMetric):  # ty:ignore[invalid-method-override]
        today = date.today()
        month_start = today.replace(day=1)
        first_day = month_start - timedelta(days=month_start.weekday())

        for col, txt in enumerate("LMMJVSD"):
            pos_x = MARGIN + col * (CELL_SPACING + CELL_WIDTH)

            draw_text(
                draw,
                (pos_x + (CELL_WIDTH + 1) // 2, MARGIN - 2),
                Font.SMALL,
                txt,
                anchor="mt",
                color=CD,
            )

        for row in range(5):
            for col in range(7):
                day = first_day + timedelta(days=row * 7 + col)
                events = ics.on_date(day)
                cell_x = MARGIN + col * (CELL_SPACING + CELL_WIDTH)
                cell_y = MARGIN + row * (CELL_SPACING + CELL_HEIGHT) + 8

                primary_color = CB
                background_color = CW
                border_color = CB

                if day == today:
                    primary_color = CW
                    background_color = CB
                    border_color = CB
                elif day.month != today.month:
                    primary_color = CL
                    border_color = None
                elif day < today:
                    primary_color = CL
                    border_color = CL

                if border_color is not None:
                    draw.rounded_rectangle(
                        xy=(
                            cell_x,
                            cell_y,
                            cell_x + CELL_WIDTH - 1,
                            cell_y + CELL_HEIGHT - 1,
                        ),
                        radius=2,
                        outline=border_color,
                        fill=background_color,
                    )

                draw_text(
                    draw,
                    (cell_x + (CELL_WIDTH + 1) // 2, cell_y + 5),
                    Font.SMALL,
                    str(day.day),
                    anchor="mt",
                    color=primary_color,
                )

                if any(event.is_full_day(day) for event in events):
                    line_pos_y = cell_y + 2

                    # If the only full day events are birthdays, draw a dashed line
                    only_birthday = not any(
                        event.is_full_day(day)
                        and summary_to_category(event.summary) != "present"
                        for event in events
                    )

                    draw.point(
                        [
                            (x, line_pos_y)
                            for x in range(
                                cell_x + 2,
                                cell_x + CELL_WIDTH - 2,
                                2 if only_birthday else 1,
                            )
                        ],
                        fill=primary_color,
                    )

                for event in events:
                    if event.is_full_day(day):
                        continue

                    period = event.day_period(day)
                    rect_x = cell_x + 2 + 3 * period.value
                    rect_y = cell_y + 14

                    draw.rectangle(
                        (rect_x, rect_y, rect_x + 1, rect_y + 1),
                        fill=primary_color,
                    )
