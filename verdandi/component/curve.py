from typing import Callable

from PIL.ImageDraw import ImageDraw

from verdandi.util.draw import points_for_shade, xy_to_bounds


def draw_curve(
    draw: ImageDraw,
    xy: tuple[int, int, int, int],
    curve: Callable[[float], float],
    progress: float = 1.0,
):
    (x_min, x_max), (y_min, y_max) = xy_to_bounds(xy)
    x_separator = x_min + int((x_max - x_min) * progress)

    min_height = [
        y_min + int((y_max - y_min) * (1.0 - curve((x - x_min) / (x_max - x_min))))
        for x in range(x_min, x_max + 1)
    ]

    # Draw the outline of the curve
    draw.point([(x_min + dx, y) for dx, y in enumerate(min_height)])

    # Draw a vertical dashed line at progress position
    draw.point(
        [
            (x_separator, y)
            for y in range(min_height[x_separator - x_min], y_max + 1)
            if (y - y_min) % 3 < 2
        ]
    )

    # Draw the pre-separator part of the curve
    if x_separator > x_min:
        draw.point(
            [
                (x, y)
                for (x, y) in points_for_shade(
                    (x_min, y_min, x_separator - 1, y_max), 8
                )
                if y >= min_height[x - x_min]
            ]
        )

    # Draw the post-separator part of the curve
    if x_separator < x_max:
        draw.point(
            [
                (x, y)
                for (x, y) in points_for_shade(
                    (x_separator + 1, y_min, x_max, y_max), 16
                )
                if y >= min_height[x - x_min]
            ]
        )
