import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import ClassVar, Self

import aiohttp
from PIL import Image
from PIL.ImageDraw import ImageDraw
from pydantic import BaseModel
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from verdandi.metric.abs_metric import MetricConfig
from verdandi.util.common import executor
from verdandi.util.color import CW
from verdandi.util.date import next_time_cadenced

logger = logging.getLogger(__name__)


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
        draw.fontmode = "1"
        self.draw(draw, **kwargs)
        return res

    async def render(self, http: aiohttp.ClientSession) -> Image.Image:
        @retry(
            retry=retry_if_exception_type(aiohttp.ClientConnectorDNSError),
            stop=stop_after_attempt(6),
            wait=wait_exponential(min=1, max=8),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        async def load_metric[M](
            metric_config: MetricConfig[M],
            http: aiohttp.ClientSession,
        ) -> M:
            return await metric_config.load(http)

        # Fetch all metrics
        metric_values = await asyncio.gather(
            *(
                load_metric(metric_config, http)
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
