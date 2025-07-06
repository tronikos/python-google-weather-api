"""Exceptions for Google Weather API."""


class GoogleWeatherApiError(Exception):
    """Exception talking to the Google Weather API."""


class GoogleWeatherApiConnectionError(GoogleWeatherApiError):
    """Exception connecting to the Google Weather API."""


class GoogleWeatherApiResponseError(GoogleWeatherApiError):
    """Exception raised for errors in the Google Weather API response."""
