import math

from PIL import Image


def _shade_filter(xy: tuple[int, int], spacing: int) -> bool:
    x, y = xy
    u, v = 7, 11
    return (u * x + v * y) % spacing == 0


def point_on_circle(
    center: tuple[int, int],
    radius: int,
    angle: float,
) -> tuple[int, int]:
    c_x, c_y = center

    return (
        c_x + int(radius * math.cos(math.pi * angle / 180.0)),
        c_y + int(radius * math.sin(math.pi * angle / 180.0)),
    )


def xy_to_bounds(
    xy: tuple[int, int, int, int],
) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    Convert a list of coords (x1, y1, x2, y2) to bounds
    ((x_min, x_max), (y_min, y_max)).
    """
    x_min, x_max = min(xy[0::2]), max(xy[0::2])
    y_min, y_max = min(xy[1::2]), max(xy[1::2])
    return ((x_min, x_max), (y_min, y_max))


def _pattern(x: int, y: int, spacing: int) -> bool:
    return (x + y * 8) % spacing == 0


def fill_with_shade(img: Image.Image, xy: tuple[int, int], spacing: int = 2):
    """
    Fill the area around input point with a shade.
    """
    todo = [xy]
    seen = {xy}

    while todo:
        x, y = todo.pop()

        if img.getpixel((x, y)) == 0:
            continue

        if _shade_filter((x, y), spacing):
            img.putpixel((x, y), 0)

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbour = (x + dx, y + dy)

            if neighbour not in seen:
                todo.append(neighbour)
                seen.add(neighbour)


def points_for_shade(
    xy: tuple[int, int, int, int],
    spacing: int = 2,
) -> list[tuple[int, int]]:
    """
    Return a list of points to color to asign a rectangle with a shade of gray.
    """

    (x_min, x_max), (y_min, y_max) = xy_to_bounds(xy)

    return [
        (x, y)
        for x in range(x_min, x_max + 1)
        for y in range(y_min, y_max + 1)
        if _shade_filter((x, y), spacing)
    ]
