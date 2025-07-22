from datetime import date

from PIL.ImageDraw import ImageDraw

from verdandi.widget.abs_widget import Widget
from verdandi.component.text import Font, draw_text
from verdandi.component.progress import draw_progress


MARGIN = 6


class Countdown2x1(Widget):
    name = "countdown-2x1"
    width = 252
    height = 111

    title: str
    date_start: date
    date_end: date

    def draw(self, draw: ImageDraw):
        now = date.today()

        if now < self.date_end:
            remaining = (self.date_end - now).days
            text = f"{remaining} jours restants"
        else:
            elapsed = (now - self.date_end).days
            text = f"{elapsed} jours passés"

        progress = min(
            1.0,
            (now - self.date_start) / (self.date_end - self.date_start),
        )

        draw_text(draw, (MARGIN, 1), Font.LARGE_BOLD, self.title)
        draw_text(draw, (MARGIN, 25), Font.LARGE, text)
        draw_progress(draw, (20, 60, self.width - 20, 90), progress)
