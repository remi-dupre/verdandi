from enum import Enum, auto
from functools import cached_property

from PIL import ImageFont
from PIL.ImageDraw import ImageDraw

from util.common import DIR_DATA

DIR_FONTS = DIR_DATA / "fonts"


class Font(Enum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()
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
            case self.LARGE:
                name = "FiraSans-Regular"
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

