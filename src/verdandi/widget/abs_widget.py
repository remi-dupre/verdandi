import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import ClassVar, Self

import aiohttp
from PIL import Image
from PIL.ImageDraw import ImageDraw
from pydantic import BaseModel

from verdandi.metric.abs_metric import MetricConfig
from verdandi.util.common import executor
from verdandi.util.color import CW
from verdandi.util.date import next_time_cadenced


class Widget(ABC, BaseModel):
    name: ClassVar[str]
    size: ClassVar[tuple[int, int]]

    @classmethod
    def width(cls) -> int:
        return 133 * cls.size[0]

    @classmethod
    def height(cls) -> int:
        return 120 * cls.size[1]

    def next_update(self, now: datetime) -> datetime:
        """
        Return the next time this widget wishes to be updated at.
        """
        return next_time_cadenced(now, timedelta(hours=6))

    @classmethod
    @abstractmethod
    def example(cls) -> Self:
        raise NotImplementedError

    @abstractmethod
    def draw(self, draw: ImageDraw, *args, **kwargs):
        raise NotImplementedError

    def _init_and_draw(self, **kwargs):
        res = Image.new(mode="L", size=(self.width(), self.height()), color=CW)
        draw = ImageDraw(res)
        self.draw(draw, **kwargs)
        return res

    async def render(self, http: aiohttp.ClientSession) -> Image.Image:
        # Fetch all metrics
        metric_values = await asyncio.gather(
            *(
                metric_config.load(http)
                for metric_config in map(
                    lambda field: getattr(self, field, None),
                    type(self).model_fields,
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
