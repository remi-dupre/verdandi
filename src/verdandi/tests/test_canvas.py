from uuid import uuid4

import pytest
from httpx import AsyncClient


async def test_direct(client: AsyncClient):
    resp = await client.get("/canvas/direct/")
    assert resp.status_code == 200


@pytest.mark.parametrize("wait", ["false", "true"])
async def test_async(client: AsyncClient, wait: str):
    resp_new = await client.get("/canvas/new/", params={"wait": wait})
    assert resp_new.status_code == 200
    data_new = resp_new.json()
    assert data_new["ready"] == (wait == "true")
    entry_id = data_new["entry_id"]

    resp_get = await client.get(f"/canvas/get/{entry_id}/")
    assert resp_get.status_code == 200


async def test_get_unknown(client: AsyncClient):
    entry_id = uuid4()
    resp = await client.get(f"/canvas/get/{entry_id}/")
    assert resp.status_code == 404
