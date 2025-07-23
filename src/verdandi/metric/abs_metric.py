from abc import ABC
from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel

M = TypeVar("M")


class MetricConfig(ABC, BaseModel, Generic[M]):
    async def load(self) -> M:
        raise NotImplementedError


class Metric(ABC, BaseModel):
    name: ClassVar[str]
