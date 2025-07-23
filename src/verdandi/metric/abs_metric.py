from abc import ABC, abstractclassmethod
from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel

M = TypeVar("M")


class MetricConfig(ABC, BaseModel, Generic[M]):
    @abstractclassmethod
    async def load(self) -> M:
        raise NotImplementedError


class Metric(BaseModel):
    name: ClassVar[str]
