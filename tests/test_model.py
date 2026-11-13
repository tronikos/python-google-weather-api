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
    (MinuteForecastResponse, "minute_forecast"),
]

_ENUMS = [
    IceThickness.Unit,
    MoonEvents.MoonPhase,
    PrecipitationProbability.PrecipitationType,
    PrecipitationSegment.DominantPrecipitationType,
    PrecipitationSegment.PrecipitationIntensity,
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
    assert parsed.daytime_forecast is not None
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


def test_daily_and_hourly_forecasts_without_records() -> None:
    """Test parsing daily and hourly forecast responses when records lists are omitted."""
    daily = DailyForecastResponse.from_dict({"timeZone": {"id": "America/New_York"}})
    assert daily.forecast_days == []
    assert "nextPageToken" not in daily.to_dict()

    hourly = HourlyForecastResponse.from_dict({"timeZone": {"id": "America/New_York"}})
    assert hourly.forecast_hours == []
    assert "nextPageToken" not in hourly.to_dict()


def test_japan_and_south_korea_current_conditions(caplog: pytest.LogCaptureFixture) -> None:
    """Test parsing current conditions with Japan/South Korea omitted and UNIT_UNSPECIFIED fields."""
    data = load_fixture("current_conditions")
    data["timeZone"] = {"id": "Asia/Tokyo", "version": ""}
    data["heatIndex"] = {"unit": "UNIT_UNSPECIFIED"}
    data["windChill"] = {"unit": "UNIT_UNSPECIFIED"}
    data["visibility"] = {"unit": "UNIT_UNSPECIFIED"}
    data["precipitation"]["snowQpf"] = {"unit": "UNIT_UNSPECIFIED"}
    data["currentConditionsHistory"]["snowQpf"] = {"unit": "UNIT_UNSPECIFIED"}
    data["wind"].pop("gust", None)
    data.pop("cloudCover", None)
    data.pop("thunderstormProbability", None)

    with caplog.at_level(logging.WARNING, logger="google_weather_api"):
        parsed = CurrentConditionsResponse.from_dict(data)

    assert caplog.records == []
    assert parsed.heat_index.degrees is None
    assert parsed.heat_index.unit is Temperature.TemperatureUnit.UNIT_UNSPECIFIED
    assert parsed.wind_chill.degrees is None
    assert parsed.visibility.distance is None
    assert parsed.visibility.unit is Visibility.Unit.UNIT_UNSPECIFIED
    assert parsed.precipitation.snow_qpf is not None
    assert parsed.precipitation.snow_qpf.quantity is None
    assert parsed.current_conditions_history.snow_qpf is not None
    assert parsed.current_conditions_history.snow_qpf.quantity is None
    assert parsed.wind.gust is None
    assert parsed.cloud_cover is None
    assert parsed.thunderstorm_probability is None
    assert CurrentConditionsResponse.from_dict(parsed.to_dict()) == parsed


def test_japan_and_south_korea_daily_forecast(caplog: pytest.LogCaptureFixture) -> None:
    """Test parsing Japan/South Korea fullDayForecast, regional condition types, and omitted fields."""
    daily_data = load_fixture("daily_forecast")
    day: dict[str, Any] = daily_data["forecastDays"][0]
    full_day = day.pop("daytimeForecast")
    day.pop("nighttimeForecast")
    full_day["weatherCondition"]["type"] = "CLOUDY_PERIODICALLY_CLEAR"
    full_day["wind"].pop("gust", None)
    full_day.pop("cloudCover", None)
    full_day.pop("thunderstormProbability", None)
    full_day["iceThickness"] = {"unit": "UNIT_UNSPECIFIED"}
    full_day["precipitation"]["snowQpf"] = {"unit": "UNIT_UNSPECIFIED"}
    day["fullDayForecast"] = full_day
    day["feelsLikeMaxTemperature"] = {"unit": "UNIT_UNSPECIFIED"}
    day["feelsLikeMinTemperature"] = {"unit": "UNIT_UNSPECIFIED"}
    day["maxHeatIndex"] = {"unit": "UNIT_UNSPECIFIED"}
    day.pop("iceThickness", None)

    with caplog.at_level(logging.WARNING, logger="google_weather_api"):
        parsed_daily = DailyForecastResponse.from_dict(daily_data)

    assert caplog.records == []
    parsed_day = parsed_daily.forecast_days[0]
    assert parsed_day.daytime_forecast is None
    assert parsed_day.nighttime_forecast is None
    assert parsed_day.full_day_forecast is not None
    assert parsed_day.full_day_forecast.weather_condition.type is WeatherCondition.Type.CLOUDY_PERIODICALLY_CLEAR
    assert parsed_day.full_day_forecast.wind.gust is None
    assert parsed_day.full_day_forecast.cloud_cover is None
    assert parsed_day.full_day_forecast.thunderstorm_probability is None
    assert parsed_day.full_day_forecast.ice_thickness is not None
    assert parsed_day.full_day_forecast.ice_thickness.thickness is None
    assert parsed_day.feels_like_max_temperature.degrees is None
    assert parsed_day.feels_like_min_temperature.degrees is None
    assert parsed_day.max_heat_index.degrees is None
    assert DailyForecastResponse.from_dict(parsed_daily.to_dict()) == parsed_daily
    assert len(WeatherCondition.Type) == 139


def test_japan_and_south_korea_hourly_forecast(caplog: pytest.LogCaptureFixture) -> None:
    """Test parsing Japan/South Korea hourly forecast with omitted and UNIT_UNSPECIFIED fields."""
    hourly_data = load_fixture("hourly_forecast_page1")
    hour: dict[str, Any] = hourly_data["forecastHours"][0]
    hour["heatIndex"] = {"unit": "UNIT_UNSPECIFIED"}
    hour["windChill"] = {"unit": "UNIT_UNSPECIFIED"}
    hour["wetBulbTemperature"] = {"unit": "UNIT_UNSPECIFIED"}
    hour["visibility"] = {"unit": "UNIT_UNSPECIFIED"}
    hour["iceThickness"] = {"unit": "UNIT_UNSPECIFIED"}
    hour["wind"].pop("gust", None)
    hour.pop("cloudCover", None)
    hour.pop("thunderstormProbability", None)

    with caplog.at_level(logging.WARNING, logger="google_weather_api"):
        parsed_hourly = HourlyForecastResponse.from_dict(hourly_data)

    assert caplog.records == []
    parsed_hour = parsed_hourly.forecast_hours[0]
    assert parsed_hour.heat_index.degrees is None
    assert parsed_hour.wind_chill.degrees is None
    assert parsed_hour.wet_bulb_temperature.degrees is None
    assert parsed_hour.visibility.distance is None
    assert parsed_hour.ice_thickness is not None
    assert parsed_hour.ice_thickness.thickness is None
    assert parsed_hour.wind.gust is None
    assert parsed_hour.cloud_cover is None
    assert parsed_hour.thunderstorm_probability is None
    assert HourlyForecastResponse.from_dict(parsed_hourly.to_dict()) == parsed_hourly
