import functools
import logging
from asyncio import Event
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Coroutine

import aiohttp
from pydantic import BaseModel

logger = logging.getLogger("uvicorn.error")


# Unique object that can serve as separator in cache keys
KWD_MARK = object()


# Types that are ignored by cache
IGNORED_TYPES = [aiohttp.ClientSession]


class CacheSlot[T](BaseModel):
    expiration: datetime
    value: T


def async_time_cache[**P1, R1](
    persistance: timedelta,
) -> Callable[[Callable[P1, Awaitable[R1]]], Callable[P1, Coroutine[None, None, R1]]]:
    """
    Ensure the function is not executed twice in a given period of time.
    """

    def decorator[**P2, R2](
        func: Callable[P2, Awaitable[R2]],
    ) -> Callable[P2, Coroutine[None, None, R2]]:
        @functools.wraps(func)
        async def wrapper(*args: P2.args, **kwargs: P2.kwargs) -> R2:
            cache_params = (*args, KWD_MARK, *sorted(kwargs.items()))

            cache_key = tuple(
                param
                for param in cache_params
                if not any(
                    isinstance(param, ignored_type) for ignored_type in IGNORED_TYPES
                )
            )

            now = datetime.now()

            # Extract stores from wrapped object
            cache_store: dict[Any, CacheSlot] = wrapper.cache_store  # ty: ignore[unresolved-attribute]
            cache_compute_events: dict[Any, Event] = wrapper.cache_compute_events  # ty: ignore[unresolved-attribute]

            # Cleanup all expired keys
            expired_keys = [
                key for key, slot in cache_store.items() if slot.expiration < now
            ]

            for key in expired_keys:
                del cache_store[key]

            # If a compute event has been created for this key, wait for the
            # computation to finish. We are not ensured that a result will be
            # added to the cache store because the computation may have raised
            # an exception.
            while compute_event := cache_compute_events.get(cache_key):
                await compute_event.wait()

            # Create a new compute event (which ensures no concurent call will
            # happen)
            compute_event = Event()
            cache_compute_events[cache_key] = compute_event

            try:
                # Fetch and update cache
                cache_slot: CacheSlot | None = cache_store.get(cache_key)

                if cache_slot is None or cache_slot.expiration < now:
                    value = await func(*args, **kwargs)
                    cache_slot = CacheSlot(expiration=now + persistance, value=value)
                    cache_store[cache_key] = cache_slot

                return cache_slot.value
            finally:
                # Notify the end of the event and clean it up
                compute_event.set()
                del cache_compute_events[cache_key]

        wrapper.cache_store: dict[Any, CacheSlot] = {}
        wrapper.cache_compute_events: dict[Any, Event] = {}
        return wrapper

    return decorator
