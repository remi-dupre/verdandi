from PIL.ImageDraw import ImageDraw

from verdandi.util.color import CL
from verdandi.util.draw import xy_to_bounds, ShadeUniform, AbcShade


def draw_vertical_pill(draw: ImageDraw, xy: tuple[int, int, int, int], progress: float):
    assert 0.0 <= progress <= 1.0
    (x_min, x_max), (y_min, y_max) = xy_to_bounds(xy)
    gauge_y = int((1.0 - progress) * (y_max - y_min) + y_min)

    if gauge_y < y_max:
        ShadeUniform(CL).fill_rect(draw, (x_min + 1, gauge_y + 1, x_max - 1, y_max - 1))

    draw.line((x_min + 1, gauge_y, x_max - 1, gauge_y))
    draw.rounded_rectangle(xy, radius=3)


def draw_progress(
    draw: ImageDraw,
    xy: tuple[int, int, int, int],
    progress: float,
    fill: AbcShade = ShadeUniform(CL),
):
    assert 0.0 <= progress <= 1.0
    (x_min, x_max), (y_min, y_max) = xy_to_bounds(xy)
    gauge_x = int(progress * (x_max - x_min) + x_min)
    draw.rounded_rectangle(xy, radius=4, width=1)
    draw.line((gauge_x, y_min, gauge_x, y_max), width=1)

    if gauge_x > x_min:
        fill.fill_area(
            draw._image,
            ((x_min + gauge_x) // 2, (y_min + y_max) // 2),
        )
