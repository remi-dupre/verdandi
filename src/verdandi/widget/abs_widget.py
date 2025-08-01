import asyncio
from abc import ABC, abstractmethod
from typing import ClassVar, Self

from PIL import Image
from PIL.ImageDraw import ImageDraw
from pydantic import BaseModel

from verdandi.metric.abs_metric import MetricConfig
from verdandi.util.common import executor


class Widget(ABC, BaseModel):
    name: ClassVar[str]
    size: ClassVar[tuple[int]]

    @property
    def width(self) -> int:
        return 133 * self.size[0]

    @property
    def height(self) -> int:
        return 120 * self.size[1]

    @classmethod
    @abstractmethod
    def example(cls) -> Self:
        raise NotImplementedError

    @abstractmethod
    def draw(self, draw: ImageDraw, *args, **kwargs):
        raise NotImplementedError

    def _init_and_draw(self, **kwargs):
        res = Image.new(mode="1", size=(self.width, self.height), color=1)
        draw = ImageDraw(res)
        self.draw(draw, **kwargs)
        return res

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

        loop = asyncio.get_event_loop()
        kwargs = {val.name: val for val in metric_values}

        return await loop.run_in_executor(
            executor,
            lambda: self._init_and_draw(**kwargs),
        )
