import functools
import logging
from time import time
from typing import Awaitable, Callable, ParamSpec, Concatenate, TypeVar


logger = logging.getLogger("uvicorn.error")

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


def log_duration_async(
    text: str,
) -> Callable[
    [Callable[Param, Awaitable[RetType]]],
    Callable[Concatenate[str, Param], Awaitable[RetType]],
]:
    def decorator(
        func: Callable[..., Awaitable[RetType]],
    ) -> Callable[..., Awaitable[RetType]]:
        @functools.wraps(func)
        async def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            start_time = time()

            try:
                res = await func(*args, **kwargs)
            finally:
                end_time = time()
                logger.info("%s: %fs", text, end_time - start_time)

            return res

        return wrapper

    return decorator
