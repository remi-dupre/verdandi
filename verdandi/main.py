from io import BytesIO
from pathlib import Path

from PIL import Image
from fastapi import FastAPI, Response


from verdandi.widget.weather import WidgetWeather3x4
from verdandi.provider.openmeteo import get_weather

app = FastAPI()


DIR_DATA = Path(__file__).parent.parent / "data"


@app.get("/")
async def generate_image():
    weather = await get_weather()
    img = Image.new(mode="1", size=(383, 223), color=1)
    WidgetWeather3x4.apply(img, (0, 0), weather)
    buffer = BytesIO()
    img.save(buffer, "png")
    buffer.seek(0)
    return Response(content=bytes(buffer.read()), media_type="image/png")
