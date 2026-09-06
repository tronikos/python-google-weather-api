"""Fixtures for the Google Weather API tests."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from google_weather_api import GoogleWeatherApi
from google_weather_api import api as api_module

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

API_KEY = "test-api-key"
REFERRER = "https://example.com/"
LATITUDE = 47.6
LONGITUDE = -122.3

_FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture recorded from the real API."""
    data: dict[str, Any] = json.loads((_FIXTURES / f"{name}.json").read_text())
    return data


@dataclass
class RecordedRequest:
    """A request received by the mock server."""

    path: str
    query: dict[str, str]
    headers: dict[str, str]


@dataclass
class MockServer:
    """A stand-in for the Google Weather API that records requests and replays responses."""

    requests: list[RecordedRequest] = field(default_factory=list)
    _responses: deque[tuple[int, Any]] = field(default_factory=deque)

    def add_response(self, payload: Any, status: int = HTTPStatus.OK) -> None:
        """Queue a response to return, in order, for the next request."""
        self._responses.append((status, payload))

    async def handle(self, request: web.Request) -> web.Response:
        """Record the request and return the next queued response."""
        self.requests.append(
            RecordedRequest(
                path=request.path,
                query=dict(request.query),
                headers=dict(request.headers),
            )
        )
        if not self._responses:
            pytest.fail(f"Unexpected request to {request.path}")
        status, payload = self._responses.popleft()
        if isinstance(payload, str):
            return web.Response(status=status, text=payload, content_type="text/html")
        return web.json_response(payload, status=status)


@pytest.fixture
async def mock_server(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[MockServer]:
    """Run a local server in place of the Google Weather API."""
    server = MockServer()
    app = web.Application()
    app.router.add_get("/{tail:.*}", server.handle)
    test_server = TestServer(app)
    await test_server.start_server()
    monkeypatch.setattr(api_module, "_BASE_URL", str(test_server.make_url("/v1")))
    yield server
    await test_server.close()


@pytest.fixture
async def session() -> AsyncGenerator[aiohttp.ClientSession]:
    """Return an aiohttp client session."""
    async with aiohttp.ClientSession() as client_session:
        yield client_session


@pytest.fixture
def api(session: aiohttp.ClientSession) -> GoogleWeatherApi:
    """Return a Google Weather API client."""
    return GoogleWeatherApi(session=session, api_key=API_KEY, referrer=REFERRER)
