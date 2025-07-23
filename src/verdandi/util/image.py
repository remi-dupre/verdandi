from io import BytesIO

from PIL import Image


def image_to_bytes(img: Image.Image) -> bytes:
    buffer = BytesIO()
    img.save(buffer, "png")
    buffer.seek(0)
    return buffer.read()
