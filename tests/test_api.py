"""Tests for the Google Weather API client."""

from __future__ import annotations

import logging
import re
from http import HTTPStatus
from typing import Any

import aiohttp
import pytest

from google_weather_api import (
    GoogleWeatherApi,
    GoogleWeatherApiAuthError,
    GoogleWeatherApiConnectionError,
    GoogleWeatherApiResponseError,
)

from .conftest import API_KEY, LATITUDE, LONGITUDE, REFERRER, MockServer, load_fixture


async def test_get_current_conditions(api: GoogleWeatherApi, mock_server: MockServer) -> None:
    """Test fetching current conditions."""
    mock_server.add_response(load_fixture("current_conditions"))

    result = await api.async_get_current_conditions(LATITUDE, LONGITUDE)

    assert result.temperature.unit == "CELSIUS"
    assert isinstance(result.temperature.degrees, float)
    assert result.time_zone.id == "America/Los_Angeles"
    assert 0 <= result.relative_humidity <= 100
    assert result.weather_condition.description.language_code == "en"
    assert mock_server.requests[0].path == "/v1/currentConditions:lookup"


async def test_request_params_and_headers(api: GoogleWeatherApi, mock_server: MockServer) -> None:
    """Test the API key, location, language, units and referrer are sent."""
    mock_server.add_response(load_fixture("current_conditions"))

    await api.async_get_current_conditions(LATITUDE, LONGITUDE)

    request = mock_server.requests[0]
    assert request.query["key"] == API_KEY
    assert request.query["location.latitude"] == str(LATITUDE)
    assert request.query["location.longitude"] == str(LONGITUDE)
    assert request.query["language_code"] == "en"
    assert request.query["units_system"] == "METRIC"
    assert request.headers[aiohttp.hdrs.REFERER] == REFERRER
    assert aiohttp.hdrs.USER_AGENT in request.headers


async def test_no_referrer_header_when_unset(session: aiohttp.ClientSession, mock_server: MockServer) -> None:
    """Test the Referer header is omitted when no referrer is configured."""
    api = GoogleWeatherApi(session=session, api_key=API_KEY)
    mock_server.add_response(load_fixture("current_conditions"))

    await api.async_get_current_conditions(LATITUDE, LONGITUDE)

    assert aiohttp.hdrs.REFERER not in mock_server.requests[0].headers


async def test_language_and_units_are_configurable(session: aiohttp.ClientSession, mock_server: MockServer) -> None:
    """Test a non-default language and units system are sent."""
    api = GoogleWeatherApi(session=session, api_key=API_KEY, language_code="el", units_system="IMPERIAL")
    mock_server.add_response(load_fixture("current_conditions"))

    await api.async_get_current_conditions(LATITUDE, LONGITUDE)

    assert mock_server.requests[0].query["language_code"] == "el"
    assert mock_server.requests[0].query["units_system"] == "IMPERIAL"


async def test_api_key_is_not_logged(api: GoogleWeatherApi, mock_server: MockServer, caplog: pytest.LogCaptureFixture) -> None:
    """Test the API key never makes it into the debug logs."""
    mock_server.add_response(load_fixture("current_conditions"))

    with caplog.at_level(logging.DEBUG, logger="google_weather_api"):
        await api.async_get_current_conditions(LATITUDE, LONGITUDE)

    assert "currentConditions:lookup" in caplog.text
    assert API_KEY not in caplog.text


async def test_get_daily_forecast(api: GoogleWeatherApi, mock_server: MockServer) -> None:
    """Test fetching the daily forecast."""
    mock_server.add_response(load_fixture("daily_forecast"))

    result = await api.async_get_daily_forecast(LATITUDE, LONGITUDE, days=2)

    assert len(result.forecast_days) == 2
    day = result.forecast_days[0]
    assert day.max_temperature.degrees >= day.min_temperature.degrees
    assert day.daytime_forecast.weather_condition.type
    assert day.nighttime_forecast.weather_condition.type
    assert day.sun_events.sunrise_time
    assert day.moon_events.moon_phase

    request = mock_server.requests[0]
    assert request.path == "/v1/forecast/days:lookup"
    assert request.query["days"] == "2"
    assert request.query["page_size"] == "2"


async def test_get_hourly_forecast_follows_pagination(api: GoogleWeatherApi, mock_server: MockServer) -> None:
    """Test hourly forecasts spanning several pages are combined into one response.

    The API caps a page at 24 records regardless of the requested page size, so
    asking for more hours than that requires following ``nextPageToken``.
    """
    page1 = load_fixture("hourly_forecast_page1")
    page2 = load_fixture("hourly_forecast_page2")
    mock_server.add_response(page1)
    mock_server.add_response(page2)

    result = await api.async_get_hourly_forecast(LATITUDE, LONGITUDE, hours=4)

    assert len(result.forecast_hours) == 4
    assert [hour.interval.start_time for hour in result.forecast_hours] == [
        hour["interval"]["startTime"] for hour in page1["forecastHours"] + page2["forecastHours"]
    ]

    first, second = mock_server.requests
    assert first.path == "/v1/forecast/hours:lookup"
    assert "page_token" not in first.query
    assert first.query["hours"] == "4"
    assert second.query["page_token"] == page1["nextPageToken"]
    assert second.query["hours"] == "4"
    assert second.query["key"] == API_KEY


async def test_hourly_forecast_stops_once_enough_records(api: GoogleWeatherApi, mock_server: MockServer) -> None:
    """Test no extra page is requested, and extra records are trimmed, once the limit is met."""
    mock_server.add_response(load_fixture("hourly_forecast_page1"))

    result = await api.async_get_hourly_forecast(LATITUDE, LONGITUDE, hours=1)

    assert len(result.forecast_hours) == 1
    assert len(mock_server.requests) == 1


async def test_pagination_stops_on_empty_page(api: GoogleWeatherApi, mock_server: MockServer) -> None:
    """Test pagination stops if a page comes back empty, rather than looping forever."""
    page1 = load_fixture("hourly_forecast_page1")
    mock_server.add_response(page1)
    mock_server.add_response({"forecastHours": [], "timeZone": page1["timeZone"], "nextPageToken": "another-token"})

    result = await api.async_get_hourly_forecast(LATITUDE, LONGITUDE, hours=48)

    assert len(result.forecast_hours) == 2
    assert len(mock_server.requests) == 2


async def test_pagination_stops_without_next_page_token(api: GoogleWeatherApi, mock_server: MockServer) -> None:
    """Test a single request is made when the API reports no further pages."""
    page = load_fixture("hourly_forecast_page1")
    del page["nextPageToken"]
    mock_server.add_response(page)

    result = await api.async_get_hourly_forecast(LATITUDE, LONGITUDE, hours=48)

    assert len(result.forecast_hours) == 2
    assert len(mock_server.requests) == 1


@pytest.mark.parametrize(
    ("status", "payload", "expected_error", "expected_message"),
    [
        (
            HTTPStatus.UNAUTHORIZED,
            {"error": {"message": "Unauthenticated."}},
            GoogleWeatherApiAuthError,
            "Unauthenticated.",
        ),
        (
            HTTPStatus.FORBIDDEN,
            {"error": {"message": "Requests from referer <empty> are blocked."}},
            GoogleWeatherApiAuthError,
            "Requests from referer <empty> are blocked.",
        ),
        (
            HTTPStatus.BAD_REQUEST,
            {
                "error": {
                    "message": "API key not valid. Please pass a valid API key.",
                    "details": [{"reason": "API_KEY_INVALID"}],
                }
            },
            GoogleWeatherApiAuthError,
            "API key not valid. Please pass a valid API key.",
        ),
        (
            HTTPStatus.BAD_REQUEST,
            {"error": {"message": "Request contains an invalid argument.", "details": [{"reason": "OTHER"}]}},
            GoogleWeatherApiResponseError,
            "Request contains an invalid argument.",
        ),
        (
            HTTPStatus.BAD_REQUEST,
            {"error": {"message": "Request contains an invalid argument."}},
            GoogleWeatherApiResponseError,
            "Request contains an invalid argument.",
        ),
        (
            HTTPStatus.TOO_MANY_REQUESTS,
            {"error": {"message": "Quota exceeded."}},
            GoogleWeatherApiResponseError,
            "Quota exceeded.",
        ),
        (
            HTTPStatus.INTERNAL_SERVER_ERROR,
            {},
            GoogleWeatherApiResponseError,
            "Unknown API error",
        ),
    ],
)
async def test_error_responses(
    api: GoogleWeatherApi,
    mock_server: MockServer,
    status: HTTPStatus,
    payload: dict[str, Any],
    expected_error: type[Exception],
    expected_message: str,
) -> None:
    """Test HTTP error responses are mapped to the right exception."""
    mock_server.add_response(payload, status=status)

    with pytest.raises(expected_error, match=re.escape(expected_message)):
        await api.async_get_current_conditions(LATITUDE, LONGITUDE)


async def test_non_json_response(api: GoogleWeatherApi, mock_server: MockServer) -> None:
    """Test a non-JSON body is reported as a connection error."""
    mock_server.add_response("<html>502 Bad Gateway</html>", status=HTTPStatus.BAD_GATEWAY)

    with pytest.raises(GoogleWeatherApiConnectionError):
        await api.async_get_current_conditions(LATITUDE, LONGITUDE)


@pytest.mark.parametrize(
    ("raised", "expected_message"),
    [
        (TimeoutError(), "Timeout"),
        (aiohttp.ClientError("boom"), "boom"),
    ],
)
async def test_connection_errors(
    api: GoogleWeatherApi,
    monkeypatch: pytest.MonkeyPatch,
    raised: Exception,
    expected_message: str,
) -> None:
    """Test transport failures are reported as connection errors."""

    def raise_error(*args: Any, **kwargs: Any) -> Any:
        raise raised

    monkeypatch.setattr(api.session, "get", raise_error)

    with pytest.raises(GoogleWeatherApiConnectionError, match=re.escape(expected_message)):
        await api.async_get_current_conditions(LATITUDE, LONGITUDE)


async def test_custom_timeout(session: aiohttp.ClientSession) -> None:
    """Test the timeout is configurable."""
    api = GoogleWeatherApi(session=session, api_key=API_KEY, timeout=30)

    assert api.timeout.total == 30
