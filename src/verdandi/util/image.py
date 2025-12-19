from io import BytesIO

from PIL import Image

from verdandi.util.color import CW, CB, CL, CD


def image_to_bytes(img: Image.Image) -> bytes:
    buffer = BytesIO()

    palette = [
        *(CB, CB, CB),
        *(CD, CD, CD),
        *(CL, CL, CL),
        *(CW, CW, CW),
    ]

    palette_img = Image.new("P", (1, 1))
    palette_img.putpalette(palette + [0] * (3 * 256 - len(palette)))
    img = img.quantize(palette=palette_img)

    img.save(buffer, "png", bits=2)
    buffer.seek(0)
    return buffer.read()
