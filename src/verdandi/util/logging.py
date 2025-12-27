import functools
import logging
from time import time
from typing import Awaitable, Callable, Coroutine


def async_log_duration[**P, R](
    logger: logging.Logger,
    text: str,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Coroutine[None, None, R]]]:
    def decorator(
        func: Callable[..., Awaitable[R]],
    ) -> Callable[..., Coroutine[None, None, R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time = time()

            try:
                res = await func(*args, **kwargs)
            finally:
                end_time = time()
                logger.info("%s: %fs", text, end_time - start_time)

            return res

        return wrapper

    return decorator
