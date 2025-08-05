import pytest
from httpx import ASGITransport, AsyncClient
from typing import AsyncGenerator

from pathlib import Path


import verdandi.configuration
from verdandi.app import app


@pytest.fixture(autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture
def base_url() -> str:
    return "http://verdandi"


@pytest.fixture
async def client(base_url: str, monkeypatch) -> AsyncGenerator[AsyncClient]:
    with monkeypatch.context() as m:
        m.setattr(
            verdandi.configuration,
            "configuration",
            verdandi.configuration.ApiConfiguration.load(
                Path(__file__).parent / "test-config.yaml"
            ),
        )

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url=base_url,
        ) as client:
            yield client
