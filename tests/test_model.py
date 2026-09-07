"""Tests for the Google Weather API models."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import pytest

from google_weather_api import (
    CurrentConditionsResponse,
    DailyForecastResponse,
    HourlyForecastResponse,
    IceThickness,
    Interval,
    MinuteForecastResponse,
    MoonEvents,
    PrecipitationProbability,
    PrecipitationSegment,
    QuantitativePrecipitationForecast,
    Temperature,
    Visibility,
    WeatherCondition,
    WindDirection,
    WindSpeed,
)

from .conftest import load_fixture

if TYPE_CHECKING:
    from google_weather_api.model import ApiStrEnum, BaseModel

_RESPONSES = [
    (CurrentConditionsResponse, "current_conditions"),
    (DailyForecastResponse, "daily_forecast"),
    (HourlyForecastResponse, "hourly_forecast_page1"),
]

_ENUMS = [
    IceThickness.Unit,
    MoonEvents.MoonPhase,
    PrecipitationProbability.PrecipitationType,
    QuantitativePrecipitationForecast.Unit,
    Temperature.TemperatureUnit,
    Visibility.Unit,
    WeatherCondition.Type,
    WindDirection.CardinalDirection,
    WindSpeed.SpeedUnit,
]


@pytest.mark.parametrize(("model", "fixture"), _RESPONSES)
def test_parses_real_responses(model: type[BaseModel], fixture: str) -> None:
    """Test responses recorded from the real API parse."""
    assert model.from_dict(load_fixture(fixture))


@pytest.mark.parametrize(("model", "fixture"), _RESPONSES)
def test_serializes_using_api_names(model: type[BaseModel], fixture: str) -> None:
    """Test to_dict uses the camelCase names the API uses."""
    parsed = model.from_dict(load_fixture(fixture))

    assert "timeZone" in parsed.to_dict()


@pytest.mark.parametrize(("model", "fixture"), _RESPONSES)
def test_round_trips(model: type[BaseModel], fixture: str) -> None:
    """Test a serialized model can be parsed back into an identical model."""
    parsed = model.from_dict(load_fixture(fixture))

    assert model.from_dict(parsed.to_dict()) == parsed


def test_deserializes_snake_case_names() -> None:
    """Test field names are accepted alongside the API's camelCase aliases."""
    parsed = Interval.from_dict({"start_time": "2026-09-06T00:00:00Z", "end_time": "2026-09-06T01:00:00Z"})

    assert parsed.start_time == "2026-09-06T00:00:00Z"
    assert parsed.end_time == "2026-09-06T01:00:00Z"


def test_ignores_unknown_fields() -> None:
    """Test fields the API adds later are ignored rather than failing the whole response."""
    data = load_fixture("current_conditions")
    data["someFieldAddedLater"] = {"nested": 1}

    assert CurrentConditionsResponse.from_dict(data).temperature.unit == "CELSIUS"


def test_unknown_enum_value_falls_back(caplog: pytest.LogCaptureFixture) -> None:
    """Test a condition type the API adds later does not fail the whole response."""
    data = load_fixture("current_conditions")
    data["weatherCondition"]["type"] = "SOME_NEW_CONDITION"

    with caplog.at_level(logging.WARNING, logger="google_weather_api"):
        parsed = CurrentConditionsResponse.from_dict(data)

    assert parsed.weather_condition.type is WeatherCondition.Type.TYPE_UNSPECIFIED
    assert parsed.temperature.unit == "CELSIUS"
    assert "SOME_NEW_CONDITION" in caplog.text


@pytest.mark.parametrize("enum", _ENUMS)
def test_enums_fall_back_to_unspecified(enum: type[ApiStrEnum]) -> None:
    """Test every enum tolerates unknown values.

    The fallback returns the first member, so guard the convention that it is the
    ``*_UNSPECIFIED`` one.
    """
    first = next(iter(enum))

    assert first.name.endswith("UNSPECIFIED")
    assert enum("VALUE_ADDED_BY_GOOGLE_LATER") is first
    assert enum(None) is first  # type: ignore[arg-type]


def test_optional_fields_may_be_absent() -> None:
    """Test fields the API omits, for example in polar regions, are optional."""
    data = load_fixture("daily_forecast")
    day: dict[str, Any] = data["forecastDays"][0]
    day["sunEvents"] = {}
    day["moonEvents"] = {"moonPhase": "FULL_MOON"}
    day.pop("iceThickness", None)
    day["daytimeForecast"].pop("iceThickness", None)
    day["daytimeForecast"]["precipitation"].pop("snowQpf", None)
    day["interval"].pop("endTime", None)

    parsed = DailyForecastResponse.from_dict(data).forecast_days[0]

    assert parsed.sun_events.sunrise_time is None
    assert parsed.sun_events.sunset_time is None
    assert parsed.moon_events.moonrise_times == []
    assert parsed.moon_events.moonset_times == []
    assert parsed.ice_thickness is None
    assert parsed.daytime_forecast.ice_thickness is None
    assert parsed.daytime_forecast.precipitation.snow_qpf is None
    assert parsed.interval.end_time is None


def test_next_page_token_is_optional() -> None:
    """Test the pagination token is absent on the last page."""
    data = load_fixture("daily_forecast")
    data.pop("nextPageToken", None)

    assert DailyForecastResponse.from_dict(data).next_page_token is None


def test_minute_forecast_segment_defaults() -> None:
    """Test parsing a minute forecast where proto3-default segment fields are omitted."""
    response = MinuteForecastResponse.from_dict(
        {
            "overallPredictionTimeframe": {"startTime": "2026-08-11T14:17:00Z"},
            "timeZone": {"id": "America/New_York"},
            "segments": [{"timeFrame": {"startTime": "2026-08-11T14:16:00Z"}, "type": "NONE"}],
        }
    )
    segment = response.segments[0]
    assert segment.type is PrecipitationSegment.DominantPrecipitationType.NONE
    assert segment.probability == 0
    assert segment.qpf is None
    assert segment.snowfall_amount is None
    assert segment.intensity is PrecipitationSegment.PrecipitationIntensity.PRECIPITATION_INTENSITY_UNSPECIFIED
    assert response.next_page_token is None


def test_minute_forecast_without_segments() -> None:
    """Test parsing a minute forecast response where the segments list is omitted."""
    response = MinuteForecastResponse.from_dict(
        {
            "overallPredictionTimeframe": {"startTime": "2026-08-11T14:17:00Z"},
            "timeZone": {"id": "America/New_York"},
        }
    )
    assert response.segments == []
