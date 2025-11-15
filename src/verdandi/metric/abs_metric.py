from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar

import aiohttp
from pydantic import BaseModel

M = TypeVar("M")


class MetricConfig(ABC, BaseModel, Generic[M]):
    @classmethod
    @abstractmethod
    async def load(self, http: aiohttp.ClientSession) -> M:
        raise NotImplementedError


class Metric(BaseModel):
    name: ClassVar[str]
