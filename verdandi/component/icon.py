from functools import cache

from PIL import Image
from PIL.ImageDraw import ImageDraw

from verdandi.util.common import DIR_DATA
from verdandi.metric.weather import WeatherCode


DIR_ICONS = DIR_DATA / "icons"


@cache
def _load_icon(icon_name: str) -> Image.Image:
    img = Image.open(DIR_ICONS / (icon_name + ".png"))
    return img.convert(mode="1")


def draw_icon(draw: ImageDraw, xy: tuple[int, int], icon_name: str):
    icon = _load_icon(icon_name)
    draw._image.paste(icon, xy)


# Runtime checks

for code in WeatherCode:
    assert (DIR_ICONS / f"small-{code.value}.png").exists(), f"no small icon for {code}"
    assert (DIR_ICONS / f"large-{code.value}.png").exists(), f"no large icon for {code}"
