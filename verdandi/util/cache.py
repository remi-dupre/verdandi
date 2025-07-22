from asyncio import Lock
from datetime import timedelta, datetime
import functools
import logging
from typing import Awaitable, Callable, ParamSpec, Concatenate, TypeVar


logger = logging.getLogger("uvicorn.error")

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


def time_cache_async(
    persistance: timedelta,
) -> Callable[
    [Callable[Param, Awaitable[RetType]]],
    Callable[Concatenate[str, Param], Awaitable[RetType]],
]:
    def decorator(
        func: Callable[..., Awaitable[RetType]],
    ) -> Callable[..., Awaitable[RetType]]:
        @functools.wraps(func)
        async def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
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
