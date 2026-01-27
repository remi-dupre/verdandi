import asyncio
from datetime import datetime, date, time, timedelta, UTC

import pytest
import time_machine

from verdandi.util.cache import async_time_cache


async def test_cache_over_time():
    @async_time_cache(timedelta(hours=1))
    async def get_time() -> datetime:
        await asyncio.sleep(0.01)
        return datetime.now(UTC).replace(second=0, microsecond=0)

    d = date(2025, 7, 1)
    t1 = datetime.combine(d, time(12, 0), tzinfo=UTC)
    t2 = datetime.combine(d, time(12, 20), tzinfo=UTC)
    t3 = datetime.combine(d, time(13, 1), tzinfo=UTC)

    with time_machine.travel(t1):
        assert await get_time() == t1

    with time_machine.travel(t2):
        assert await get_time() == t1

    with time_machine.travel(t3):
        assert await get_time() == t3


async def test_cache_after_crash():
    class FirstCrash(Exception): ...

    @async_time_cache(timedelta(hours=1))
    async def crash_once() -> int:
        num_calls = getattr(crash_once, "num_calls", 0) + 1
        setattr(crash_once, "num_calls", num_calls)
        await asyncio.sleep(0.01)

        if num_calls == 1:
            raise FirstCrash("It will crash once")

        return num_calls

    d = date(2025, 7, 1)
    t1 = datetime.combine(d, time(12, 0), tzinfo=UTC)
    t2 = datetime.combine(d, time(12, 20), tzinfo=UTC)
    t3 = datetime.combine(d, time(13, 1), tzinfo=UTC)
    t4 = datetime.combine(d, time(13, 21), tzinfo=UTC)

    with time_machine.travel(t1):
        with pytest.raises(FirstCrash):
            await crash_once()

    # First successful run, start the timer
    with time_machine.travel(t2):
        assert await crash_once() == 2

    # The timer is not yet expired (because it starts at t2, not t1)
    with time_machine.travel(t3):
        assert await crash_once() == 2

    # The timer expired
    with time_machine.travel(t4):
        assert await crash_once() == 3


async def test_concurrent_crash():
    class FirstCrash(Exception): ...

    @async_time_cache(timedelta(hours=1))
    async def crash_once() -> int:
        num_calls = getattr(crash_once, "num_calls", 0) + 1
        setattr(crash_once, "num_calls", num_calls)
        await asyncio.sleep(0.01)

        if num_calls == 1:
            raise FirstCrash("It will crash once")

        return num_calls

    d = date(2025, 7, 1)
    t1 = datetime.combine(d, time(12, 0), tzinfo=UTC)
    t2 = datetime.combine(d, time(12, 20), tzinfo=UTC)
    t3 = datetime.combine(d, time(13, 1), tzinfo=UTC)

    with time_machine.travel(t1):
        task_1 = asyncio.create_task(crash_once())
        await asyncio.sleep(0.0)
        task_2 = asyncio.create_task(crash_once())
        task_3 = asyncio.create_task(crash_once())

        with pytest.raises(FirstCrash):
            await task_1

        assert await task_2 == 2
        assert await task_3 == 2

    with time_machine.travel(t2):
        assert await crash_once() == 2

    with time_machine.travel(t3):
        assert await crash_once() == 3
