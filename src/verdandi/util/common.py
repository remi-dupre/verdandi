from abc import abstractmethod
from typing import Protocol
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DIR_DATA = Path(__file__).parent.parent.parent / "static"

executor = ThreadPoolExecutor(max_workers=4)


class Comparable(Protocol):
    @abstractmethod
    def __lt__(self, other, /) -> bool: ...


def min_max[T: Comparable](x: T, y: T) -> tuple[T, T]:
    return min(x, y), max(x, y)
