"""API for Google Weather."""

from __future__ import annotations

from http import HTTPStatus
import logging
from typing import Any

import aiohttp

from .exceptions import (
    GoogleWeatherApiConnectionError,
    GoogleWeatherApiResponseError,
)
from .model import (
    CurrentConditionsResponse,
    DailyForecastResponse,
    HourlyForecastResponse,
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
        except TimeoutError as err:
            raise GoogleWeatherApiConnectionError("Timeout") from err
        except aiohttp.ClientError as err:
            raise GoogleWeatherApiConnectionError(err) from err

    async def async_get_current_conditions(
        self, latitude: float, longitude: float
    ) -> CurrentConditionsResponse:
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

    async def async_get_hourly_forecast(
        self, latitude: float, longitude: float, hours: int = 48
    ) -> HourlyForecastResponse:
        """Fetch hourly weather forecast.

        See https://developers.google.com/maps/documentation/weather/reference/rest/v1/forecast.hours/lookup
        """
        data = await self._async_get(
            "forecast/hours:lookup",
            {
                "location.latitude": latitude,
                "location.longitude": longitude,
                "hours": hours,
                "page_size": hours,
            },
        )
        return HourlyForecastResponse.from_dict(data)

    async def async_get_daily_forecast(
        self, latitude: float, longitude: float, days: int = 10
    ) -> DailyForecastResponse:
        """Fetch daily weather forecast.

        See https://developers.google.com/maps/documentation/weather/reference/rest/v1/forecast.days/lookup
        """
        data = await self._async_get(
            "forecast/days:lookup",
            {
                "location.latitude": latitude,
                "location.longitude": longitude,
                "days": days,
                "page_size": days,
            },
        )
        return DailyForecastResponse.from_dict(data)
