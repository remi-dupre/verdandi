from PIL.ImageDraw import ImageDraw

from verdandi.util.draw import AbcShade, point_on_circle
from verdandi.util.color import CW

ANGLE_START = 135
ANGLE_END = 405


def draw_gauge(
    draw: ImageDraw,
    xy: tuple[int, int],
    radius_ext: int,
    radius_inn: int,
    sections: list[tuple[float, AbcShade | None]] = [(1.0, None)],
):
    assert radius_ext > radius_inn

    x, y = xy
    bounds_ext = (x - radius_ext, y - radius_ext, x + radius_ext, y + radius_ext)
    bounds_inn = (x - radius_inn, y - radius_inn, x + radius_inn, y + radius_inn)

    # Draw exterior arc
    draw.pieslice(bounds_ext, ANGLE_START, ANGLE_END, width=2)

    # Draw wheel spokes for each progress step
    prev_angle = ANGLE_START

    for progress, shade in sections:
        curr_angle = ANGLE_START + (ANGLE_END - ANGLE_START) * progress
        draw.pieslice(bounds_ext, prev_angle, curr_angle, width=1)

        if shade is not None and curr_angle > prev_angle:
            shade.fill_area(
                draw._image,
                point_on_circle(
                    xy,
                    (radius_inn + radius_ext) // 2,
                    (prev_angle + curr_angle) // 2,
                ),
            )

        prev_angle = curr_angle

    # Erase wheel spokes and draw inner arc
    draw.ellipse(bounds_inn, fill=CW)
    draw.arc(bounds_inn, ANGLE_START, ANGLE_END, width=2)
