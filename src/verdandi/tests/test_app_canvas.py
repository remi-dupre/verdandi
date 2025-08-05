from uuid import uuid4

import time_machine
import pytest
from httpx import AsyncClient


async def test_direct(client: AsyncClient):
    resp = await client.get("/canvas/direct/")
    assert resp.status_code == 200


@pytest.mark.parametrize("wait", ["false", "true"])
async def test_async(client: AsyncClient, wait: str):
    resp_new = await client.get("/canvas/redirect/", params={"wait": wait})
    assert resp_new.status_code == 200
    data_new = resp_new.json()
    url = data_new["url"]

    # A few more requests to fill the registry
    await client.get("/canvas/redirect/", params={"wait": wait})
    await client.get("/canvas/redirect/", params={"wait": wait})

    resp_get = await client.get(url)
    assert resp_get.status_code == 200


async def test_get_unknown(client: AsyncClient):
    entry_id = uuid4()
    resp = await client.get(f"/canvas/get/{entry_id}/")
    assert resp.status_code == 404


async def test_registry(client: AsyncClient):
    time_create = "2025-07-01 11:00"
    time_fetch_valid = "2025-07-01 11:55"
    time_fetch_invalid = "2025-07-01 18:00"

    with time_machine.travel(time_create):
        resp_new = await client.get("/canvas/redirect/")
        data_new = resp_new.json()
        fetch_url = data_new["url"]

    async def is_valid() -> bool:
        resp = await client.get(fetch_url)
        return resp.status_code == 200

    with time_machine.travel(time_create):
        assert await is_valid()

    with time_machine.travel(time_fetch_valid):
        assert await is_valid()

    with time_machine.travel(time_fetch_invalid):
        assert not await is_valid()
