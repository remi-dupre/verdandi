from datetime import datetime, timedelta

from PIL.ImageDraw import ImageDraw

from verdandi.widget.abs_widget import Widget
from verdandi.component.gauge import draw_gauge
from verdandi.component.text import draw_text, Font
from verdandi.component.icon import draw_icon
from verdandi.metric.velib import VelibMetric, VelibConfig
from verdandi.util.draw import ShadeMatrix, ShadeUniform
from verdandi.util.color import CW, CL, CD
from verdandi.util.date import next_time_cadenced

FILL_MECHANICAL = ShadeMatrix([CD, CL], [CL, CD])
FILL_ELECTRIC = ShadeMatrix([CW, CL], [CL, CW])


class Velib1x1(Widget):
    name = "velib-1x1"
    size = (1, 1)
    velib: VelibConfig

    def next_update(self, now: datetime) -> datetime:
        return next_time_cadenced(now, timedelta(hours=3))

    @classmethod
    def example(cls) -> "Velib1x1":
        return Velib1x1(velib=VelibConfig(station_id=213686196))

    def draw(self, draw: ImageDraw, velib: VelibMetric):  # ty:ignore[invalid-method-override]
        occupied = velib.mechanical + velib.electric

        draw_gauge(
            draw,
            (60, 52),
            50,
            38,
            [
                (velib.mechanical / velib.capacity, FILL_MECHANICAL),
                ((velib.mechanical + velib.electric) / velib.capacity, FILL_ELECTRIC),
                (1.0, ShadeUniform(CW)),
            ],
        )

        draw_text(
            draw,
            (60, 52),
            Font.LARGE_BOLD,
            f"{occupied}/{velib.capacity}",
            anchor="mm",
        )

        draw_icon(draw, (43, 68), "custom-bike")
        draw_text(draw, (60, 98), Font.SMALL, velib.station_name.upper(), anchor="mm")
