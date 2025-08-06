from asyncio import Lock
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

            # Fetch and update cache
            async with wrapper.lock:
                cache_slot: CacheSlot | None = wrapper.cache_store.get(cache_key)

                if cache_slot is not None and cache_slot.expiration >= now:
                    return cache_slot.value

                value = await func(*args, **kwargs)

                wrapper.cache_store[cache_key] = CacheSlot(
                    expiration=now + persistance,
                    value=value,
                )

                return value

            return wrapper.cache_value

        wrapper.lock = Lock()
        wrapper.cache_store = {}
        return wrapper

    return decorator
