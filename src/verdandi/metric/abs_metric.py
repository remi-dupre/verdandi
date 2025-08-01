from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel

M = TypeVar("M")


class MetricConfig(ABC, BaseModel, Generic[M]):
    @classmethod
    @abstractmethod
    async def load(self) -> M:
        raise NotImplementedError


class Metric(BaseModel):
    name: ClassVar[str]
