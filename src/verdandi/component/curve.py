from typing import Callable

from PIL.ImageDraw import ImageDraw

from verdandi.util.draw import points_for_shade, xy_to_bounds


def draw_curve(
    draw: ImageDraw,
    xy: tuple[int, int, int, int],
    curve: Callable[[float], float],
    shade_parts: list[tuple[float, int]] = [(1.0, 16)],
):
    assert len(shade_parts) > 0
    (x_min, x_max), (y_min, y_max) = xy_to_bounds(xy)

    min_height = [
        y_min + int((y_max - y_min) * (1.0 - curve((x - x_min) / (x_max - x_min))))
        for x in range(x_min, x_max + 1)
    ]

    # Draw the outline of the curve
    draw.point([(x_min + dx, y) for dx, y in enumerate(min_height)])
    draw.point([(x_min + dx, y - 1) for dx, y in enumerate(min_height)])

    # Draw each section with its own density
    prev_cursor = 0.0

    for cursor, density in shade_parts:
        x_start = x_min + int((x_max - x_min) * prev_cursor)
        x_end = x_min + int((x_max - x_min) * cursor)
        prev_cursor = cursor

        draw.point(
            [
                (x, y)
                for (x, y) in points_for_shade(
                    (x_start, y_min, x_end - 1, y_max),
                    density,
                )
                if y >= min_height[x - x_min]
            ]
        )
