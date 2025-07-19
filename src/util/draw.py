import math


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


def points_for_shade(
    xy: tuple[int, int, int, int],
    spacing: int = 2,
) -> list[tuple[int, int]]:
    """
    Return a list of points to color to asign a rectangle with a shade of gray.
    """

    (x_min, x_max), (y_min, y_max) = xy_to_bounds(xy)

    match spacing:
        case _:
            u, v = 7, 11

    return [
        (x, y)
        for x in range(x_min, x_max + 1)
        for y in range(y_min, y_max + 1)
        if (u * x + v * y) % spacing == 0
    ]
