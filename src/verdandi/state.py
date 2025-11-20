import asyncio
from datetime import datetime, timedelta
from functools import cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Response
from pydantic import BaseModel, Field


from verdandi.configuration import ApiConfiguration

MAX_REGISTRY_DURATION: timedelta = timedelta(hours=3)


class RegistryEntry(BaseModel, arbitrary_types_allowed=True):
    request_time: datetime
    response: asyncio.Task[Response]

    def is_obsolete(self, now: datetime) -> bool:
        return (now - self.request_time) > MAX_REGISTRY_DURATION

    async def fetch(self, now: datetime) -> Response | None:
        if self.is_obsolete(now):
            return None

        return await self.response


class AppState(BaseModel, arbitrary_types_allowed=True):
    configuration: ApiConfiguration = Field(default_factory=ApiConfiguration.load)
    response_registry: dict[UUID, RegistryEntry] = Field(default_factory=dict)
    response_registry_lock: asyncio.Lock = Field(default_factory=asyncio.Lock)

    async def clear_registry(self, now: datetime | None = None):
        if now is None:
            now = datetime.now()

        async with self.response_registry_lock:
            popped_keys = {
                key
                for key, val in self.response_registry.items()
                if val.is_obsolete(now)
            }

            for key in popped_keys:
                del self.response_registry[key]

    async def get_response(self, entry_id: UUID) -> Response | None:
        now = datetime.now()
        entry = self.response_registry.get(entry_id)

        if entry is None:
            return None

        return await entry.fetch(now)

    async def set_response(self, entry_id: UUID, task: asyncio.Task[Response]):
        now = datetime.now()
        await self.clear_registry(now)
        entry = RegistryEntry(request_time=now, response=task)

        async with self.response_registry_lock:
            self.response_registry[entry_id] = entry

    @staticmethod
    @cache
    def get_shared_state():
        return AppState()


DepState = Annotated[AppState, Depends(AppState.get_shared_state)]
