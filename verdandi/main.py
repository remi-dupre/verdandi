from io import BytesIO
from pathlib import Path

from PIL import Image
from fastapi import FastAPI, Response

from verdandi.configuration import configuration
from verdandi.metric.weather import WeatherConfig
from verdandi.widget.weather import WeatherRecap3x2

app = FastAPI()


DIR_DATA = Path(__file__).parent.parent / "data"


@app.get("/")
async def generate_image():
    widget = WeatherRecap3x2(
        weather=WeatherConfig(
            lat=48.8534,
            lon=2.3488,
            timezone="Europe/Paris",
        )
    )

    img = Image.new(mode="1", size=configuration.size, color=1)

    for widget in configuration.widgets:
        await widget.config.apply(img, widget.position)

    buffer = BytesIO()
    img.save(buffer, "png")
    buffer.seek(0)
    return Response(content=bytes(buffer.read()), media_type="image/png")
