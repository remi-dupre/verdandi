from abc import ABC, abstractmethod
import math
from typing import Iterable
from collections import defaultdict

from PIL import Image
from PIL.ImageDraw import ImageDraw


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


class AbcShade(ABC):
    @abstractmethod
    def color_at(self, xy: tuple[int, int]) -> int:
        raise NotImplementedError

    def draw_points(self, draw: ImageDraw, points: Iterable[tuple[int, int]]):
        """
        Draw a set of points with this shade.
        """
        points_for_color = defaultdict(list)
        points = list(points)

        for xy in points:
            color = self.color_at(xy)
            points_for_color[color].append(xy)

        for color, points in points_for_color.items():
            draw.point(points, fill=color)

    def fill_rect(self, draw: ImageDraw, xy: tuple[int, int, int, int]):
        """
        Fill a full rectangle with this shade.
        """
        (x_min, x_max), (y_min, y_max) = xy_to_bounds(xy)

        self.draw_points(
            draw,
            ((x, y) for x in range(x_min, x_max + 1) for y in range(y_min, y_max + 1)),
        )

    def fill_area(self, img: Image.Image, xy: tuple[int, int]):
        """
        Fill the area around input point with this shade.
        """
        back_color = img.getpixel(xy)
        todo = [xy]
        seen = {xy}

        while todo:
            x, y = todo.pop()

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbour = (x + dx, y + dy)

                if neighbour not in seen and img.getpixel(neighbour) == back_color:
                    todo.append(neighbour)
                    seen.add(neighbour)

        self.draw_points(ImageDraw(img), seen)


class ShadeUniform(AbcShade):
    """
    A uniform color.
    """

    def __init__(self, color: int):
        self.color = color

    def color_at(self, xy: tuple[int, int]) -> int:
        return self.color


class ShadeMatrix(AbcShade):
    """
    A repeating pattern.
    """

    def __init__(self, *matrix: list[int]):
        self.matrix = list(matrix)

    def color_at(self, xy: tuple[int, int]) -> int:
        x, y = xy
        row = y % len(self.matrix)
        col = x % len(self.matrix[row])
        return self.matrix[row][col]
