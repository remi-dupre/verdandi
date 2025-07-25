import asyncio
from abc import ABC, abstractmethod, abstractclassmethod
from typing import ClassVar, Self

from PIL import Image
from PIL.ImageDraw import ImageDraw
from pydantic import BaseModel

from verdandi.metric.abs_metric import MetricConfig


class Widget(ABC, BaseModel):
    name: ClassVar[str]
    width: ClassVar[int]
    height: ClassVar[int]

    @abstractclassmethod
    def example(cls) -> Self:
        raise NotImplementedError

    @abstractmethod
    def draw(self, draw: ImageDraw, *args, **kwargs):
        raise NotImplementedError

    async def render(self) -> Image.Image:
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

        # Daw in a temporary buffer
        res = Image.new(mode="1", size=(self.width, self.height), color=1)
        draw = ImageDraw(res)
        self.draw(draw, **kwargs)
        return res
