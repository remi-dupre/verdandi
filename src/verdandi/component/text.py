from enum import Enum, auto
from functools import cached_property

from pydantic import BaseModel
from PIL import ImageFont
from PIL.ImageDraw import ImageDraw

from verdandi.util.common import DIR_DATA

DIR_FONTS = DIR_DATA / "fonts"


class Font(Enum):
    SMALL = auto()
    MEDIUM = auto()
    XMEDIUM = auto()
    XMEDIUM_BOLD = auto()
    LARGE = auto()
    LARGE_BOLD = auto()
    XLARGE = auto()

    @cached_property
    def font(self) -> ImageFont.FreeTypeFont:
        match self:
            case self.SMALL:
                name = "MacExtendedMinecraft"
                size = 8
            case self.MEDIUM:
                name = "PixelOperatorHB"
                size = 16
            case self.XMEDIUM:
                name = "FiraSans-Regular"
                size = 20
            case self.XMEDIUM_BOLD:
                name = "FiraSans-Bold"
                size = 20
            case self.LARGE:
                name = "FiraSans-Regular"
                size = 24
            case self.LARGE_BOLD:
                name = "FiraSans-Bold"
                size = 24
            case self.XLARGE:
                name = "FiraSans-Regular"
                size = 64

        return ImageFont.truetype(
            DIR_FONTS / (name + ".woff2"),
            size,
        )


def draw_text(
    draw: ImageDraw,
    xy: tuple[int, int],
    font: Font,
    text: str,
    anchor="la",
):
    draw.text(xy, text, font=font.font, fill=0, anchor=anchor)


def size_text(
    draw: ImageDraw,
    font: Font,
    text: str,
) -> int:
    return int(draw.textlength(text, font=font.font))


class TextArea(BaseModel, arbitrary_types_allowed=True):
    draw: ImageDraw
    bounds: tuple[int, int, int, int | None]
    line_height: int
    cursor: tuple[int, int] = (0, 0)

    @property
    def bounds_width(self) -> int:
        return abs(self.bounds[2] - self.bounds[0])

    @property
    def height(self) -> int:
        if self.cursor[0] == 0:
            return self.cursor[1]
        else:
            return self.cursor[1] + self.line_height

    def _try_draw_on_line(self, font: Font, text: str) -> bool:
        draw_width = size_text(self.draw, font, text)

        if self.bounds_width < self.cursor[0] + draw_width:
            return False

        draw_text(
            self.draw,
            (
                self.bounds[0] + self.cursor[0],
                self.bounds[1] + self.cursor[1] + self.line_height // 2,
            ),
            font,
            text,
            anchor="lm",
        )
        self.cursor = (self.cursor[0] + draw_width, self.cursor[1])
        return True

    def draw_text(self, font: Font, text: str, /, breakable: bool = True):
        if breakable:
            unbreakable_chunks = text.split()
        else:
            unbreakable_chunks = [text]

        for chunk in unbreakable_chunks:
            if self.cursor[0] != 0:
                space_size = size_text(self.draw, font, " ")

                self.cursor = (
                    min(self.cursor[0] + space_size, self.bounds_width),
                    self.cursor[1],
                )

            if not self._try_draw_on_line(font, chunk):
                self.cursor = (0, self.cursor[1] + self.line_height)

                if self.bounds[3] is None or self.bounds[3] < self.cursor[1]:
                    self._try_draw_on_line(font, chunk)
