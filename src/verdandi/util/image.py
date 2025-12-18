from io import BytesIO

from PIL import Image


def image_to_bytes(img: Image.Image) -> bytes:
    buffer = BytesIO()
    img = img.quantize(colors=4)
    img.save(buffer, "png", bits=2)
    buffer.seek(0)
    return buffer.read()
