import re
import os
import pytest
import json
from typing import AsyncGenerator
from unittest import mock
from pathlib import Path
from contextlib import asynccontextmanager

import aiohttp
import time_machine
from aioresponses import aioresponses
from httpx import ASGITransport, AsyncClient


from verdandi.app import app
from verdandi.state import AppState

FIXTURES_PATH = Path(__file__).parent / "fixtures"


@asynccontextmanager
async def get_mocked_http() -> AsyncGenerator[aiohttp.ClientSession, None]:
    async with aiohttp.ClientSession() as http:
        with (
            time_machine.travel("2025-11-15 19:15"),
            aioresponses() as mock,
        ):
            with open(FIXTURES_PATH / "open-meteo.json") as f:
                mock.get(
                    re.compile("^https://api.open-meteo.com/v1/forecast.*$"),
                    payload=json.load(f),
                    repeat=True,
                )

            with open(FIXTURES_PATH / "velib" / "station_information.json") as f:
                mock.get(
                    re.compile(
                        "^https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json$"
                    ),
                    payload=json.load(f),
                    repeat=True,
                )

            with open(FIXTURES_PATH / "velib" / "station_status.json") as f:
                mock.get(
                    re.compile(
                        "^https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json$"
                    ),
                    payload=json.load(f),
                    repeat=True,
                )

            with open(FIXTURES_PATH / "ics" / "french-holidays.ics") as f:
                mock.get(
                    re.compile("^https://calendar-url/french-holidays.ics$"),
                    body=f.read(),
                    repeat=True,
                )

            with open(FIXTURES_PATH / "ics" / "schedule.ics") as f:
                mock.get(
                    re.compile("^https://calendar-url/schedule.ics$"),
                    body=f.read(),
                    repeat=True,
                )

            yield http


@pytest.fixture
async def http() -> AsyncGenerator[aiohttp.ClientSession]:
    async with get_mocked_http() as http:
        yield http


@pytest.fixture(autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture
def base_url() -> str:
    return "http://verdandi"


@pytest.fixture
def secret() -> str:
    return "this-is-the-secret"


@pytest.fixture
async def client(base_url: str, monkeypatch, http) -> AsyncGenerator[AsyncClient]:
    test_config_path = FIXTURES_PATH / "test-config.yaml"
    test_env = {"VERDANDI_CONFIG_FILE": str(test_config_path)}

    with mock.patch.dict(os.environ, test_env, clear=True):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url=base_url,
        ) as client:
            yield client


@pytest.fixture
async def client_with_secret(
    base_url: str,
    secret: str,
    http: aiohttp.ClientSession,
    monkeypatch,
) -> AsyncGenerator[AsyncClient]:
    test_config_path = FIXTURES_PATH / "test-config.yaml"
    state = AppState.get_shared_state()

    test_env = {
        "VERDANDI_CONFIG_FILE": str(test_config_path),
        "VERDANDI_SECRET": secret,
    }

    with (
        mock.patch.dict(os.environ, test_env, clear=True),
        mock.patch.object(state.configuration, "use_secret", True),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url=base_url,
        ) as client:
            yield client
