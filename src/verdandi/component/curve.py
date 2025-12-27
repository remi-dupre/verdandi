from typing import Callable

from PIL.ImageDraw import ImageDraw

from verdandi.util.color import CB, CL
from verdandi.util.draw import xy_to_bounds, AbcShade, ShadeUniform
from verdandi.component.text import draw_text, Font
from verdandi.util.common import min_max


def draw_curve(
    draw: ImageDraw,
    xy: tuple[int, int, int, int],
    curve: Callable[[float], float],
    shade_parts: list[tuple[float, AbcShade]] = [(1.0, ShadeUniform(CB))],
    y_scale: list[tuple[str, float, AbcShade]] = [],
    y_origin: float = 0.0,
):
    assert len(shade_parts) > 0
    (x_min, x_max), (y_min, y_max) = xy_to_bounds(xy)
    y_origin_coord = y_min + int((y_max - y_min) * (1.0 - y_origin))

    min_height = [
        y_min + int((y_max - y_min) * (1.0 - curve((x - x_min) / (x_max - x_min))))
        for x in range(x_min, x_max + 1)
    ]

    # Draw each section with its own density
    prev_cursor = 0.0

    for cursor, shade in shade_parts:
        assert prev_cursor <= cursor <= 1.0
        x_start = x_min + int((x_max - x_min) * prev_cursor)
        x_end = x_min + int((x_max - x_min) * cursor)
        prev_cursor = cursor

        shade.draw_points(
            draw,
            (
                (x, y)
                for x in range(x_start, x_end + 1)
                for y in range(*min_max(min_height[x - x_min], y_origin_coord + 1))
            ),
        )

    # Draw intermediary lines
    for label, scale_pos, shade in y_scale:
        scale_y = y_min + int((y_max - y_min) * (1.0 - scale_pos)) + 2
        shade.fill_rect(draw, (x_min, scale_y, x_max, scale_y + 1))
        draw_text(draw, (x_min, scale_y), Font.SMALL, label, anchor="rm", color=CL)

    # Draw the outline of the curve
    draw.point([(x_min + dx, y) for dx, y in enumerate(min_height)])
    draw.point([(x_min + dx, y - 1) for dx, y in enumerate(min_height)])
