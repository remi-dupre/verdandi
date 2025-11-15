from asyncio import Event
from datetime import timedelta, datetime
import functools
import logging
from typing import Awaitable, Callable

from pydantic import BaseModel


logger = logging.getLogger("uvicorn.error")


# Unique object that can serve as separator in cache keys
KWD_MARK = object()


class CacheSlot[T](BaseModel):
    expiration: datetime
    value: T


def async_time_cache[**P, R](
    persistance: timedelta,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """
    Ensure the function is not executed twice in a given period of time.
    """

    def decorator(
        func: Callable[..., Awaitable[R]],
    ) -> Callable[..., Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            cache_key = (*args, KWD_MARK, *sorted(kwargs.items()))
            now = datetime.now()

            # Cleanup all expired keys
            expired_keys = [
                key
                for key, slot in wrapper.cache_store.items()
                if slot.expiration < now
            ]

            for key in expired_keys:
                del wrapper.cache_store[key]

            # If a compute event has been created for this key, wait for the
            # computation to finish and return the resulting cache key.
            if compute_event := wrapper.cache_compute_events.get(cache_key):
                await compute_event.wait()
                return wrapper.cache_store[cache_key].value

            # Create a new compute event (which ensures no concurent call will
            # happen)
            compute_event = Event()
            wrapper.cache_compute_events[cache_key] = compute_event

            # Fetch and update cache
            cache_slot: CacheSlot | None = wrapper.cache_store.get(cache_key)

            if cache_slot is None or cache_slot.expiration < now:
                value = await func(*args, **kwargs)
                cache_slot = CacheSlot(expiration=now + persistance, value=value)
                wrapper.cache_store[cache_key] = cache_slot

            # Notify the end of the event and clean it up
            compute_event.set()
            del wrapper.cache_compute_events[cache_key]
            return cache_slot.value

        wrapper.cache_store = {}
        wrapper.cache_compute_events = {}
        return wrapper

    return decorator
