from PIL.ImageDraw import ImageDraw

from verdandi.util.draw import xy_to_bounds, points_for_shade


def draw_vertical_pill(draw: ImageDraw, xy: tuple[int, int, int, int], progress: float):
    assert 0.0 <= progress <= 1.0
    (x_min, x_max), (y_min, y_max) = xy_to_bounds(xy)
    gauge_y = int((1.0 - progress) * (y_max - y_min) + y_min)

    draw.rounded_rectangle(xy, radius=3)
    draw.line((x_min + 1, gauge_y, x_max - 1, gauge_y))

    if gauge_y < y_max:
        draw.point(points_for_shade((x_min + 1, gauge_y + 1, x_max - 1, y_max - 1)))
