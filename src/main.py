from pathlib import Path

from PIL import Image

from widget.weather import WidgetWeather3x4


DIR_DATA = Path(__file__).parent.parent / "data"


def main():
    img = Image.new(mode="1", size=(383, 223), color=1)
    WidgetWeather3x4.apply(img, (0, 0))
    img.save("test.png")


if __name__ == "__main__":
    main()
