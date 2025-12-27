import logging
from io import BytesIO

from PIL import Image

from verdandi.util.color import CW, CB, CL, CD


logger = logging.getLogger(__name__)


def validate_palette(img: Image.Image) -> bool:
    palette = {CW, CB, CL, CD}

    return all(
        img.getpixel((x, y)) in palette
        for x in range(img.size[0])
        for y in range(img.size[1])
    )


def invalid_colors(img: Image.Image) -> set[int]:
    palette = {CW, CB, CL, CD}

    return {
        img.getpixel((x, y))
        for x in range(img.size[0])
        for y in range(img.size[1])
        if img.getpixel((x, y)) not in palette
    }  # ty:ignore[invalid-return-type]


def image_to_bytes(img: Image.Image) -> bytes:
    if not validate_palette(img):
        logger.warning("Found pixels outside of color palette")

    palette = [
        *(CB, CB, CB),
        *(CD, CD, CD),
        *(CL, CL, CL),
        *(CW, CW, CW),
    ]

    palette_img = Image.new("P", (1, 1))
    palette_img.putpalette(palette + [0] * (3 * 256 - len(palette)))
    img = img.quantize(palette=palette_img)

    buffer = BytesIO()
    img.save(buffer, "png", bits=2)
    buffer.seek(0)
    return buffer.read()
