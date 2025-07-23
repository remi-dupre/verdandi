from asyncio import Lock
from datetime import timedelta, datetime
import functools
import logging
from typing import Awaitable, Callable


logger = logging.getLogger("uvicorn.error")


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
            async with wrapper.lock:
                now = datetime.now()

                if wrapper.cache_time is None or wrapper.cache_time + persistance < now:
                    wrapper.cache_time = now
                    wrapper.cache_value = await func(*args, **kwargs)

            return wrapper.cache_value

        wrapper.lock = Lock()
        wrapper.cache_time = None
        wrapper.cache_value = None
        return wrapper

    return decorator
