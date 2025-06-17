"""API for Google Weather."""

from __future__ import annotations

from http import HTTPStatus
import logging
from typing import Any

import aiohttp


class GoogleWeatherApiError(Exception):
    """Exception talking to the Google Weather API."""


class GoogleWeatherApiConnectionError(GoogleWeatherApiError):
    """Exception connecting to the Google Weather API."""


class GoogleWeatherApiResponseError(GoogleWeatherApiError):
    """Exception raised for errors in the Google Weather API response."""


_LOGGER = logging.getLogger(__name__)

_BASE_URL = "https://weather.googleapis.com/v1"
_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"


class GoogleWeatherApi:
    """Class to interact with the Google Weather API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
        latitude: float,
        longitude: float,
        language_code: str = "en",
        units_system: str = "METRIC",
        referrer: str | None = None,
        timeout: int = 10,
    ) -> None:
        """Initialize the Google Weather API client."""
        self.session = session
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.language_code = language_code
        self.units_system = units_system
        self.referrer = referrer
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def _async_get(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """Perform a GET request."""
        url = f"{_BASE_URL}/{endpoint}"
        headers = {aiohttp.hdrs.USER_AGENT: _USER_AGENT}
        if self.referrer:
            headers[aiohttp.hdrs.REFERER] = self.referrer
        params = {
            **params,
            "key": self.api_key,
            "language_code": self.language_code,
            "units_system": self.units_system,
            "location.latitude": self.latitude,
            "location.longitude": self.longitude,
        }
        _LOGGER.debug("GET %s with params: %s", url, params)
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
                    raise GoogleWeatherApiResponseError(res["error"]["message"])
                return res
        except (aiohttp.ClientError, TimeoutError) as err:
            raise GoogleWeatherApiConnectionError(
                f"Error connecting to API: {err}"
            ) from err

    async def async_get_current_conditions(self) -> dict[str, Any]:
        """Fetch current weather conditions."""
        return await self._async_get(
            "currentConditions:lookup",
            {},
        )

    async def async_get_hourly_forecast(self, hours: int = 48) -> dict[str, Any]:
        """Fetch hourly weather forecast."""
        return await self._async_get(
            "forecast/hours:lookup",
            {
                "hours": hours,
                "page_size": hours,
            },
        )

    async def async_get_daily_forecast(self, days: int = 10) -> dict[str, Any]:
        """Fetch daily weather forecast."""
        return await self._async_get(
            "forecast/days:lookup",
            {
                "days": days,
                "page_size": days,
            },
        )
