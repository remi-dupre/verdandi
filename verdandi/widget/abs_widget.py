import asyncio
from abc import ABC, abstractclassmethod
from typing import ClassVar

from PIL import Image
from PIL.ImageDraw import ImageDraw
from pydantic import BaseModel

from verdandi.metric.abs_metric import MetricConfig


class Widget(ABC, BaseModel):
    name: ClassVar[str]
    width: ClassVar[int]
    height: ClassVar[int]

    async def apply(self, img: Image.Image, xy: tuple[int, int]):
        # Fetch all metrics
        metric_values = await asyncio.gather(
            *(
                metric_config.load()
                for metric_config in map(
                    lambda field: getattr(self, field, None),
                    self.model_fields,
                )
                if isinstance(metric_config, MetricConfig)
            )
        )

        kwargs = {val.name: val for val in metric_values}
        tmp_img = Image.new(mode="1", size=(self.width, self.height), color=1)

        # Daw in a temporary buffer and then paste at appropriate location
        draw = ImageDraw(tmp_img)
        self.draw(draw, **kwargs)
        img.paste(tmp_img, xy)

    @abstractclassmethod
    def draw(cls, draw: ImageDraw, xy: tuple[int, int], *args, **kwargs):
        raise NotImplementedError
