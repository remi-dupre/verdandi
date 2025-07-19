from PIL import Image
from abc import ABC, abstractclassmethod

from PIL.ImageDraw import ImageDraw


class Widget(ABC):
    name: str
    width: int
    height: int

    @classmethod
    def apply(cls, img: Image.Image, xy: tuple[int, int]):
        tmp_img = Image.new(mode="1", size=(cls.width, cls.height), color=1)
        draw = ImageDraw(tmp_img)
        cls.draw(draw)
        img.paste(tmp_img, xy)

    @abstractclassmethod
    def draw(cls, draw: ImageDraw, xy: tuple[int, int]):
        raise NotImplementedError
