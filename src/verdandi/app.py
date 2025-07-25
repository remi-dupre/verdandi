import logging
import asyncio
from pathlib import Path

from PIL import Image
from fastapi import FastAPI, Response

from verdandi.configuration import configuration
from verdandi.util.logging import async_log_duration
from verdandi.util.image import image_to_bytes

app = FastAPI()
logger = logging.getLogger(__name__)


DIR_DATA = Path(__file__).parent.parent / "data"


@app.get("/")
@async_log_duration(logger, "Generate canvas")
async def generate_image():
    # Render all widgets concurently
    widget_imgs = await asyncio.gather(
        *(widget.config.render() for widget in configuration.widgets)
    )

    # Paste rendered widgets to appropriate locations in a canvas
    img = Image.new(mode="1", size=configuration.size, color=1)

    for widget, widget_img in zip(configuration.widgets, widget_imgs):
        img.paste(widget_img, widget.position)

    # Encode image to a buffer and respond
    return Response(
        content=image_to_bytes(img),
        media_type="image/png",
    )
