"""API for Google Weather."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

import aiohttp

from .exceptions import (
    GoogleWeatherApiAuthError,
    GoogleWeatherApiConnectionError,
    GoogleWeatherApiResponseError,
)
from .model import (
    CurrentConditionsResponse,
    DailyForecastResponse,
    HourlyForecastResponse,
    MinuteForecastResponse,
)

_LOGGER = logging.getLogger(__name__)

_BASE_URL = "https://weather.googleapis.com/v1"
_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"


class GoogleWeatherApi:
    """Class to interact with the Google Weather API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
        language_code: str = "en",
        units_system: str = "METRIC",
        referrer: str | None = None,
        timeout: int = 10,
    ) -> None:
        """Initialize the Google Weather API client."""
        self.session = session
        self.api_key = api_key
        self.language_code = language_code
        self.units_system = units_system
        self.referrer = referrer
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def _async_get(self, endpoint: str, params: dict[str, Any], *, include_language_code: bool = True) -> dict[str, Any]:
        """Perform a GET request."""
        url = f"{_BASE_URL}/{endpoint}"
        headers = {aiohttp.hdrs.USER_AGENT: _USER_AGENT}
        if self.referrer:
            headers[aiohttp.hdrs.REFERER] = self.referrer
        params = {
            **params,
            "units_system": self.units_system,
        }
        if include_language_code:
            params["language_code"] = self.language_code
        # Log before adding the API key so it doesn't end up in debug logs.
        _LOGGER.debug("GET %s with params: %s", url, params)
        params["key"] = self.api_key
        try:
            async with self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
            ) as resp:
                res: dict[str, Any] = await resp.json()
                _LOGGER.debug("Got %s for %s", resp.status, url)
                if resp.status != HTTPStatus.OK:
                    error_data = res.get("error", {})
                    error_msg = error_data.get("message", "Unknown API error")

                    if resp.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                        raise GoogleWeatherApiAuthError(error_msg)

                    # Google APIs often return 400 Bad Request for invalid API keys
                    if resp.status == HTTPStatus.BAD_REQUEST:
                        for detail in error_data.get("details", []):
                            if detail.get("reason") == "API_KEY_INVALID":
                                raise GoogleWeatherApiAuthError(error_msg)

                    raise GoogleWeatherApiResponseError(error_msg)
                return res
        except TimeoutError as err:
            raise GoogleWeatherApiConnectionError("Timeout") from err
        except aiohttp.ClientError as err:
            raise GoogleWeatherApiConnectionError(err) from err

    async def _async_get_all_pages(
        self,
        endpoint: str,
        params: dict[str, Any],
        records_key: str,
        limit: int,
        *,
        include_language_code: bool = True,
    ) -> dict[str, Any]:
        """Perform a GET request, following pagination until `limit` records are collected.

        The API caps the number of records it returns per page (24 for hourly forecasts),
        regardless of the requested page size, so a single request is not enough.
        """
        params = {**params, "page_size": limit}
        data = await self._async_get(endpoint, params, include_language_code=include_language_code)
        records: list[Any] = data.get(records_key, [])
        while len(records) < limit and (page_token := data.get("nextPageToken")):
            data = await self._async_get(
                endpoint, {**params, "page_token": page_token}, include_language_code=include_language_code
            )
            page_records: list[Any] = data.get(records_key, [])
            if not page_records:
                break
            records.extend(page_records)
        data[records_key] = records[:limit]
        return data

    async def async_get_current_conditions(self, latitude: float, longitude: float) -> CurrentConditionsResponse:
        """Fetch current weather conditions.

        See https://developers.google.com/maps/documentation/weather/reference/rest/v1/currentConditions/lookup
        """
        data = await self._async_get(
            "currentConditions:lookup",
            {
                "location.latitude": latitude,
                "location.longitude": longitude,
            },
        )
        return CurrentConditionsResponse.from_dict(data)

    async def async_get_hourly_forecast(self, latitude: float, longitude: float, hours: int = 48) -> HourlyForecastResponse:
        """Fetch hourly weather forecast.

        See https://developers.google.com/maps/documentation/weather/reference/rest/v1/forecast.hours/lookup
        """
        data = await self._async_get_all_pages(
            "forecast/hours:lookup",
            {
                "location.latitude": latitude,
                "location.longitude": longitude,
                "hours": hours,
            },
            "forecastHours",
            hours,
        )
        return HourlyForecastResponse.from_dict(data)

    async def async_get_daily_forecast(self, latitude: float, longitude: float, days: int = 10) -> DailyForecastResponse:
        """Fetch daily weather forecast.

        See https://developers.google.com/maps/documentation/weather/reference/rest/v1/forecast.days/lookup
        """
        data = await self._async_get_all_pages(
            "forecast/days:lookup",
            {
                "location.latitude": latitude,
                "location.longitude": longitude,
                "days": days,
            },
            "forecastDays",
            days,
        )
        return DailyForecastResponse.from_dict(data)

    async def async_get_minute_forecast(self, latitude: float, longitude: float, minutes: int = 360) -> MinuteForecastResponse:
        """Fetch minute-by-minute precipitation nowcast for up to 6 hours.

        The endpoint does not accept language_code (a reserved field in google.maps.weather.v1),
        so it is omitted from these requests.

        See https://developers.google.com/maps/documentation/weather/minute-forecast
        """
        data = await self._async_get_all_pages(
            "forecast/minutes:lookup",
            {
                "location.latitude": latitude,
                "location.longitude": longitude,
            },
            "segments",
            minutes,
            include_language_code=False,
        )
        return MinuteForecastResponse.from_dict(data)
