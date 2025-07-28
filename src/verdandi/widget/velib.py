from PIL.ImageDraw import ImageDraw

from verdandi.widget.abs_widget import Widget
from verdandi.component.gauge import draw_gauge
from verdandi.component.text import draw_text, Font
from verdandi.component.icon import draw_icon
from verdandi.metric.velib import VelibMetric, VelibConfig


class Velib1x1(Widget):
    name = "velib-1x1"
    size = (1, 1)
    velib: VelibConfig

    @classmethod
    def example(cls) -> "Velib1x1":
        return Velib1x1(velib=VelibConfig(station_id=213686196))

    def draw(self, draw: ImageDraw, velib: VelibMetric):
        occupied = velib.mechanical + velib.electric

        draw_gauge(
            draw,
            (60, 52),
            50,
            38,
            [
                (velib.mechanical / velib.capacity, 2),
                ((velib.mechanical + velib.electric) / velib.capacity, 5),
                (1.0, None),
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
