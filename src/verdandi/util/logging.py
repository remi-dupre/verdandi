import functools
import logging
from time import time
from typing import Awaitable, Callable, Coroutine


def async_log_duration[**P1, R1](
    logger: logging.Logger,
    text: str,
) -> Callable[[Callable[P1, Awaitable[R1]]], Callable[P1, Coroutine[None, None, R1]]]:
    def decorator[**P2, R2](
        func: Callable[P2, Awaitable[R2]],
    ) -> Callable[P2, Coroutine[None, None, R2]]:
        @functools.wraps(func)
        async def wrapper(*args: P2.args, **kwargs: P2.kwargs) -> R2:
            start_time = time()

            try:
                res = await func(*args, **kwargs)
            finally:
                end_time = time()
                logger.info("%s: %fs", text, end_time - start_time)

            return res

        return wrapper

    return decorator
