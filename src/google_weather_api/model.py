"""Models for the Google Weather API."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum

from mashumaro.config import BaseConfig
from mashumaro.mixins.json import DataClassJSONMixin

_LOGGER = logging.getLogger(__name__)


class ApiStrEnum(StrEnum):
    """A StrEnum that tolerates values the API added after this library was released.

    Google keeps adding values to these enums. Rather than failing to parse the whole
    response, an unknown value falls back to the first member, which is by convention
    the ``*_UNSPECIFIED`` one.
    """

    @classmethod
    def _missing_(cls, value: object) -> ApiStrEnum:
        """Fall back to the unspecified member for values not known to this library."""
        unspecified = next(iter(cls))
        _LOGGER.warning(
            "Unknown %s value %r returned by the API, falling back to %s. "
            "Please report this at https://github.com/tronikos/python-google-weather-api/issues",
            cls.__name__,
            value,
            unspecified,
        )
        return unspecified


class BaseModel(DataClassJSONMixin):
    """Base class for all models."""

    class Config(BaseConfig):
        """Serialize using the camelCase names the API uses, so models round-trip."""

        serialize_by_alias = True
        allow_deserialization_not_by_alias = True
        omit_none = True


@dataclass
class AirPressure(BaseModel):
    """Represents the atmospheric air pressure conditions."""

    mean_sea_level_millibars: float = field(metadata={"alias": "meanSeaLevelMillibars"})
    """The mean sea level air pressure in millibars."""


@dataclass
class Interval(BaseModel):
    """Represents a time interval."""

    start_time: str = field(metadata={"alias": "startTime"})
    """Inclusive start of the interval in RFC 3339 format."""

    end_time: str | None = field(default=None, metadata={"alias": "endTime"})
    """Optional. Exclusive end of the interval in RFC 3339 format."""


@dataclass
class TimeZone(BaseModel):
    """Represents a time zone from the IANA Time Zone Database."""

    id: str
    """IANA Time Zone Database time zone. For example "America/New_York"."""

    version: str | None = None
    """Optional. IANA Time Zone Database version number. For example "2019a"."""


@dataclass
class LocalizedText(BaseModel):
    """Localized variant of a text in a particular language."""

    text: str
    """Localized string in the language corresponding to languageCode below."""

    language_code: str = field(metadata={"alias": "languageCode"})
    """The text's BCP-47 language code, such as "en-US" or "sr-Latn"."""


@dataclass
class Temperature(BaseModel):
    """Represents a temperature value."""

    class TemperatureUnit(ApiStrEnum):
        """Represents a unit used to measure temperatures."""

        UNIT_UNSPECIFIED = "UNIT_UNSPECIFIED"
        CELSIUS = "CELSIUS"
        FAHRENHEIT = "FAHRENHEIT"

    degrees: float | None = None
    """The temperature value (in degrees) in the specified unit."""

    unit: TemperatureUnit = TemperatureUnit.UNIT_UNSPECIFIED
    """The code for the unit used to measure the temperature value."""


@dataclass
class QuantitativePrecipitationForecast(BaseModel):
    """Represents the expected amount of melted precipitation."""

    class Unit(ApiStrEnum):
        """Represents the unit used to measure the amount of accumulated precipitation."""

        UNIT_UNSPECIFIED = "UNIT_UNSPECIFIED"
        MILLIMETERS = "MILLIMETERS"
        INCHES = "INCHES"

    quantity: float | None = None
    """The amount of precipitation, measured as liquid water equivalent."""

    unit: Unit = Unit.UNIT_UNSPECIFIED
    """The code of the unit used to measure the amount of accumulated precipitation."""


@dataclass
class PrecipitationProbability(BaseModel):
    """Represents the probability of precipitation at a given location."""

    class PrecipitationType(ApiStrEnum):
        """Represents the type of precipitation at a given location."""

        TYPE_UNSPECIFIED = "TYPE_UNSPECIFIED"
        NONE = "NONE"
        SNOW = "SNOW"
        RAIN = "RAIN"
        LIGHT_RAIN = "LIGHT_RAIN"
        HEAVY_RAIN = "HEAVY_RAIN"
        RAIN_AND_SNOW = "RAIN_AND_SNOW"
        SLEET = "SLEET"
        FREEZING_RAIN = "FREEZING_RAIN"
        PRECIPITATION_TYPE_HAIL = "PRECIPITATION_TYPE_HAIL"

    type: PrecipitationType
    """A code that indicates the type of precipitation."""

    percent: int
    """A percentage from 0 to 100 that indicates the chances of precipitation."""


@dataclass
class Precipitation(BaseModel):
    """Represents a set of precipitation values at a given location."""

    probability: PrecipitationProbability
    """The probability of precipitation (values from 0 to 100)."""

    qpf: QuantitativePrecipitationForecast
    """The amount of precipitation (rain or snow), measured as liquid water."""

    snow_qpf: QuantitativePrecipitationForecast | None = field(default=None, metadata={"alias": "snowQpf"})
    """The amount of snow accumulation, measured as liquid water equivalent."""


@dataclass
class WindSpeed(BaseModel):
    """Represents the speed of the wind."""

    class SpeedUnit(ApiStrEnum):
        """Represents the unit used to measure speed."""

        UNIT_UNSPECIFIED = "UNIT_UNSPECIFIED"
        KILOMETERS_PER_HOUR = "KILOMETERS_PER_HOUR"
        MILES_PER_HOUR = "MILES_PER_HOUR"

    value: float | None = None
    """The value of the wind speed."""

    unit: SpeedUnit = SpeedUnit.UNIT_UNSPECIFIED
    """The code that represents the unit used to measure the wind speed."""


@dataclass
class WindDirection(BaseModel):
    """Represents the direction from which the wind originates."""

    class CardinalDirection(ApiStrEnum):
        """Represents a cardinal direction (including ordinal directions)."""

        CARDINAL_UNSPECIFIED = "CARDINAL_UNSPECIFIED"
        NORTH = "NORTH"
        NORTH_NORTHEAST = "NORTH_NORTHEAST"
        NORTHEAST = "NORTHEAST"
        EAST_NORTHEAST = "EAST_NORTHEAST"
        EAST = "EAST"
        EAST_SOUTHEAST = "EAST_SOUTHEAST"
        SOUTHEAST = "SOUTHEAST"
        SOUTH_SOUTHEAST = "SOUTH_SOUTHEAST"
        SOUTH = "SOUTH"
        SOUTH_SOUTHWEST = "SOUTH_SOUTHWEST"
        SOUTHWEST = "SOUTHWEST"
        WEST_SOUTHWEST = "WEST_SOUTHWEST"
        WEST = "WEST"
        WEST_NORTHWEST = "WEST_NORTHWEST"
        NORTHWEST = "NORTHWEST"
        NORTH_NORTHWEST = "NORTH_NORTHWEST"

    degrees: int
    """The direction of the wind in degrees (values from 0 to 360)."""

    cardinal: CardinalDirection
    """The code that represents the cardinal direction from which the wind is blowing."""


@dataclass
class Wind(BaseModel):
    """Represents a set of wind properties."""

    direction: WindDirection
    """The direction of the wind, the angle it is coming from."""

    speed: WindSpeed
    """The speed of the wind."""

    gust: WindSpeed | None = None
    """The wind gust (sudden increase in the wind speed)."""


@dataclass
class Visibility(BaseModel):
    """Represents visibility conditions, the distance at which objects can be discerned."""

    class Unit(ApiStrEnum):
        """Represents the unit used to measure the visibility distance."""

        UNIT_UNSPECIFIED = "UNIT_UNSPECIFIED"
        KILOMETERS = "KILOMETERS"
        MILES = "MILES"

    distance: float | None = None
    """The visibility distance in the specified unit."""

    unit: Unit = Unit.UNIT_UNSPECIFIED
    """The code that represents the unit used to measure the distance."""


@dataclass
class WeatherCondition(BaseModel):
    """Represents a weather condition for a given location at a given period of time."""

    class Type(ApiStrEnum):
        """Marks the weather condition type in a forecast element's context."""

        TYPE_UNSPECIFIED = "TYPE_UNSPECIFIED"
        CLEAR = "CLEAR"
        MOSTLY_CLEAR = "MOSTLY_CLEAR"
        PARTLY_CLOUDY = "PARTLY_CLOUDY"
        MOSTLY_CLOUDY = "MOSTLY_CLOUDY"
        CLOUDY = "CLOUDY"
        WINDY = "WINDY"
        WIND_AND_RAIN = "WIND_AND_RAIN"
        LIGHT_RAIN_SHOWERS = "LIGHT_RAIN_SHOWERS"
        CHANCE_OF_SHOWERS = "CHANCE_OF_SHOWERS"
        SCATTERED_SHOWERS = "SCATTERED_SHOWERS"
        RAIN_SHOWERS = "RAIN_SHOWERS"
        HEAVY_RAIN_SHOWERS = "HEAVY_RAIN_SHOWERS"
        LIGHT_TO_MODERATE_RAIN = "LIGHT_TO_MODERATE_RAIN"
        MODERATE_TO_HEAVY_RAIN = "MODERATE_TO_HEAVY_RAIN"
        RAIN = "RAIN"
        LIGHT_RAIN = "LIGHT_RAIN"
        HEAVY_RAIN = "HEAVY_RAIN"
        RAIN_PERIODICALLY_HEAVY = "RAIN_PERIODICALLY_HEAVY"
        LIGHT_SNOW_SHOWERS = "LIGHT_SNOW_SHOWERS"
        CHANCE_OF_SNOW_SHOWERS = "CHANCE_OF_SNOW_SHOWERS"
        SCATTERED_SNOW_SHOWERS = "SCATTERED_SNOW_SHOWERS"
        SNOW_SHOWERS = "SNOW_SHOWERS"
        HEAVY_SNOW_SHOWERS = "HEAVY_SNOW_SHOWERS"
        LIGHT_TO_MODERATE_SNOW = "LIGHT_TO_MODERATE_SNOW"
        MODERATE_TO_HEAVY_SNOW = "MODERATE_TO_HEAVY_SNOW"
        SNOW = "SNOW"
        LIGHT_SNOW = "LIGHT_SNOW"
        HEAVY_SNOW = "HEAVY_SNOW"
        SNOWSTORM = "SNOWSTORM"
        SNOW_PERIODICALLY_HEAVY = "SNOW_PERIODICALLY_HEAVY"
        HEAVY_SNOW_STORM = "HEAVY_SNOW_STORM"
        BLOWING_SNOW = "BLOWING_SNOW"
        RAIN_AND_SNOW = "RAIN_AND_SNOW"
        HAIL = "HAIL"
        HAIL_SHOWERS = "HAIL_SHOWERS"
        THUNDERSTORM = "THUNDERSTORM"
        THUNDERSHOWER = "THUNDERSHOWER"
        LIGHT_THUNDERSTORM_RAIN = "LIGHT_THUNDERSTORM_RAIN"
        SCATTERED_THUNDERSTORMS = "SCATTERED_THUNDERSTORMS"
        HEAVY_THUNDERSTORM = "HEAVY_THUNDERSTORM"
        CLEAR_AFTER_FOG_IN_THE_MORNING = "CLEAR_AFTER_FOG_IN_THE_MORNING"
        CLEAR_BUT_LATER_TURNING_CLOUDY = "CLEAR_BUT_LATER_TURNING_CLOUDY"
        CLEAR_BUT_LATER_TURNING_TO_RAIN_AND_SNOW_MAIN_CONSTITUENT_RAIN = (
            "CLEAR_BUT_LATER_TURNING_TO_RAIN_AND_SNOW_MAIN_CONSTITUENT_RAIN"
        )
        CLEAR_BUT_LATER_TURNING_TO_SNOW_AND_RAIN_MAIN_CONSTITUENT_SNOW = (
            "CLEAR_BUT_LATER_TURNING_TO_SNOW_AND_RAIN_MAIN_CONSTITUENT_SNOW"
        )
        CLEAR_BUT_THUNDERSTORMS_LATER = "CLEAR_BUT_THUNDERSTORMS_LATER"
        CLEAR_IN_THE_MORNING_BUT_CLOUDY_IN_THE_EVENING = "CLEAR_IN_THE_MORNING_BUT_CLOUDY_IN_THE_EVENING"
        CLEAR_IN_THE_MORNING_WITH_BRIEF_RAIN_IN_THE_EVENING = "CLEAR_IN_THE_MORNING_WITH_BRIEF_RAIN_IN_THE_EVENING"
        CLEAR_MORNING_WITH_BRIEF_RAIN = "CLEAR_MORNING_WITH_BRIEF_RAIN"
        CLEAR_WITH_BRIEF_RAIN = "CLEAR_WITH_BRIEF_RAIN"
        CLEAR_WITH_BRIEF_RAIN_AND_SNOW_RAIN_AS_MAIN_CONSTITUENT = "CLEAR_WITH_BRIEF_RAIN_AND_SNOW_RAIN_AS_MAIN_CONSTITUENT"
        CLEAR_WITH_BRIEF_RAIN_LATER = "CLEAR_WITH_BRIEF_RAIN_LATER"
        CLEAR_WITH_BRIEF_SNOW = "CLEAR_WITH_BRIEF_SNOW"
        CLEAR_WITH_BRIEF_SNOW_AND_RAIN_SNOW_AS_MAIN_CONSTITUENT = "CLEAR_WITH_BRIEF_SNOW_AND_RAIN_SNOW_AS_MAIN_CONSTITUENT"
        CLEAR_WITH_BRIEF_SNOW_LATER = "CLEAR_WITH_BRIEF_SNOW_LATER"
        CLEAR_WITH_PERIODIC_CLOUDS_LATER = "CLEAR_WITH_PERIODIC_CLOUDS_LATER"
        CLEAR_WITH_PERIODIC_RAIN = "CLEAR_WITH_PERIODIC_RAIN"
        CLEAR_WITH_PERIODIC_RAIN_ACCOMPANIED_BY_THUNDER = "CLEAR_WITH_PERIODIC_RAIN_ACCOMPANIED_BY_THUNDER"
        CLEAR_WITH_PERIODIC_RAIN_AND_SNOW_RAIN_AS_MAIN_CONSTITUENT = (
            "CLEAR_WITH_PERIODIC_RAIN_AND_SNOW_RAIN_AS_MAIN_CONSTITUENT"
        )
        CLEAR_WITH_PERIODIC_RAIN_LATER = "CLEAR_WITH_PERIODIC_RAIN_LATER"
        CLEAR_WITH_PERIODIC_SNOW = "CLEAR_WITH_PERIODIC_SNOW"
        CLEAR_WITH_PERIODIC_SNOW_AND_RAIN_SNOW_AS_MAIN_CONSTITUENT = (
            "CLEAR_WITH_PERIODIC_SNOW_AND_RAIN_SNOW_AS_MAIN_CONSTITUENT"
        )
        CLEAR_WITH_PERIODIC_SNOW_LATER = "CLEAR_WITH_PERIODIC_SNOW_LATER"
        CLEAR_WITH_RAIN_AFTER_MIDNIGHT = "CLEAR_WITH_RAIN_AFTER_MIDNIGHT"
        CLEAR_WITH_RAIN_IN_THE_NIGHT = "CLEAR_WITH_RAIN_IN_THE_NIGHT"
        CLEAR_WITH_RAIN_LATER = "CLEAR_WITH_RAIN_LATER"
        CLEAR_WITH_SNOW_ALONG_THE_MOUNTAINS = "CLEAR_WITH_SNOW_ALONG_THE_MOUNTAINS"
        CLEAR_WITH_SNOW_LATER = "CLEAR_WITH_SNOW_LATER"
        CLEAR_WITH_THUNDERSTORMS_ALONG_THE_MOUNTAINS = "CLEAR_WITH_THUNDERSTORMS_ALONG_THE_MOUNTAINS"
        CLEAR_WITH_THUNDERSTORMS_IN_THE_AFTERNOON = "CLEAR_WITH_THUNDERSTORMS_IN_THE_AFTERNOON"
        CLOUDY_BUT_CLEAR_LATER = "CLOUDY_BUT_CLEAR_LATER"
        CLOUDY_BUT_LATER_TURNING_TO_RAIN_AND_SNOW_MAIN_CONSTITUENT_RAIN = (
            "CLOUDY_BUT_LATER_TURNING_TO_RAIN_AND_SNOW_MAIN_CONSTITUENT_RAIN"
        )
        CLOUDY_BUT_LATER_TURNING_TO_SNOW_AND_RAIN_MAIN_CONSTITUENT_SNOW = (
            "CLOUDY_BUT_LATER_TURNING_TO_SNOW_AND_RAIN_MAIN_CONSTITUENT_SNOW"
        )
        CLOUDY_BUT_PERIODICALLY_CLEAR_LATER = "CLOUDY_BUT_PERIODICALLY_CLEAR_LATER"
        CLOUDY_BUT_THUNDERSTORMS_LATER = "CLOUDY_BUT_THUNDERSTORMS_LATER"
        CLOUDY_MORNING_WITH_BRIEF_RAIN = "CLOUDY_MORNING_WITH_BRIEF_RAIN"
        CLOUDY_PERIODICALLY_CLEAR = "CLOUDY_PERIODICALLY_CLEAR"
        CLOUDY_SNOWING_IN_THE_EVENING = "CLOUDY_SNOWING_IN_THE_EVENING"
        CLOUDY_SNOWING_IN_THE_NIGHT = "CLOUDY_SNOWING_IN_THE_NIGHT"
        CLOUDY_WITH_BRIEF_RAIN = "CLOUDY_WITH_BRIEF_RAIN"
        CLOUDY_WITH_BRIEF_RAIN_AND_SNOW_RAIN_AS_MAIN_CONSTITUENT = "CLOUDY_WITH_BRIEF_RAIN_AND_SNOW_RAIN_AS_MAIN_CONSTITUENT"
        CLOUDY_WITH_BRIEF_RAIN_LATER = "CLOUDY_WITH_BRIEF_RAIN_LATER"
        CLOUDY_WITH_BRIEF_SNOW = "CLOUDY_WITH_BRIEF_SNOW"
        CLOUDY_WITH_BRIEF_SNOW_AND_RAIN_SNOW_AS_MAIN_CONSTITUENT = "CLOUDY_WITH_BRIEF_SNOW_AND_RAIN_SNOW_AS_MAIN_CONSTITUENT"
        CLOUDY_WITH_BRIEF_SNOW_LATER = "CLOUDY_WITH_BRIEF_SNOW_LATER"
        CLOUDY_WITH_BRIEF_THUNDERSTORM = "CLOUDY_WITH_BRIEF_THUNDERSTORM"
        CLOUDY_WITH_FOG_ON_THE_OCEAN_AND_AT_THE_SEASHORE = "CLOUDY_WITH_FOG_ON_THE_OCEAN_AND_AT_THE_SEASHORE"
        CLOUDY_WITH_PERIODIC_RAIN = "CLOUDY_WITH_PERIODIC_RAIN"
        CLOUDY_WITH_PERIODIC_RAIN_ACCOMPANIED_BY_THUNDER = "CLOUDY_WITH_PERIODIC_RAIN_ACCOMPANIED_BY_THUNDER"
        CLOUDY_WITH_PERIODIC_RAIN_AND_SNOW_RAIN_AS_MAIN_CONSTITUENT = (
            "CLOUDY_WITH_PERIODIC_RAIN_AND_SNOW_RAIN_AS_MAIN_CONSTITUENT"
        )
        CLOUDY_WITH_PERIODIC_RAIN_LATER = "CLOUDY_WITH_PERIODIC_RAIN_LATER"
        CLOUDY_WITH_PERIODIC_SNOW = "CLOUDY_WITH_PERIODIC_SNOW"
        CLOUDY_WITH_PERIODIC_SNOW_ACCOMPANIED_BY_THUNDER = "CLOUDY_WITH_PERIODIC_SNOW_ACCOMPANIED_BY_THUNDER"
        CLOUDY_WITH_PERIODIC_SNOW_AND_RAIN_SNOW_AS_MAIN_CONSTITUENT = (
            "CLOUDY_WITH_PERIODIC_SNOW_AND_RAIN_SNOW_AS_MAIN_CONSTITUENT"
        )
        CLOUDY_WITH_PERIODIC_SNOW_LATER = "CLOUDY_WITH_PERIODIC_SNOW_LATER"
        CLOUDY_WITH_RAIN_AFTER_MIDNIGHT = "CLOUDY_WITH_RAIN_AFTER_MIDNIGHT"
        CLOUDY_WITH_RAIN_FROM_ABOUT_NOON = "CLOUDY_WITH_RAIN_FROM_ABOUT_NOON"
        CLOUDY_WITH_RAIN_FROM_EVENING = "CLOUDY_WITH_RAIN_FROM_EVENING"
        CLOUDY_WITH_RAIN_LATER = "CLOUDY_WITH_RAIN_LATER"
        CLOUDY_WITH_SNOW_FROM_AROUND_NOON = "CLOUDY_WITH_SNOW_FROM_AROUND_NOON"
        CLOUDY_WITH_SNOW_LATER = "CLOUDY_WITH_SNOW_LATER"
        FOG = "FOG"
        RAINSNOW_MIX_LATER_BECOMING_CLEAR_RAIN_AS_MAIN = "RAINSNOW_MIX_LATER_BECOMING_CLEAR_RAIN_AS_MAIN"
        RAINSNOW_MIX_RAIN_AS_MAIN = "RAINSNOW_MIX_RAIN_AS_MAIN"
        RAINY_BUT_PERIODICALLY_CLEAR = "RAINY_BUT_PERIODICALLY_CLEAR"
        RAIN_ACCOMPANIED_BY_LIGHTNING = "RAIN_ACCOMPANIED_BY_LIGHTNING"
        RAIN_ACCOMPANIED_BY_WINDSTORM = "RAIN_ACCOMPANIED_BY_WINDSTORM"
        RAIN_CLEAR_AT_NIGHT = "RAIN_CLEAR_AT_NIGHT"
        RAIN_CLEAR_FROM_AROUND_EVENING = "RAIN_CLEAR_FROM_AROUND_EVENING"
        RAIN_CLEAR_FROM_AROUND_NOON = "RAIN_CLEAR_FROM_AROUND_NOON"
        RAIN_LATER_BECOMING_CLEAR = "RAIN_LATER_BECOMING_CLEAR"
        RAIN_LATER_BECOMING_CLOUDY = "RAIN_LATER_BECOMING_CLOUDY"
        RAIN_LATER_BECOMING_SNOW = "RAIN_LATER_BECOMING_SNOW"
        RAIN_LATER_WITH_PERIODIC_SNOW = "RAIN_LATER_WITH_PERIODIC_SNOW"
        RAIN_SNOW_AT_NIGHT = "RAIN_SNOW_AT_NIGHT"
        RAIN_SNOW_IN_THE_EVENING = "RAIN_SNOW_IN_THE_EVENING"
        RAIN_TEMPORARILY_BECOMING_SLEET = "RAIN_TEMPORARILY_BECOMING_SLEET"
        RAIN_THAT_PERIODICALLY_STOPS = "RAIN_THAT_PERIODICALLY_STOPS"
        RAIN_WITH_BRIEF_SNOW = "RAIN_WITH_BRIEF_SNOW"
        RAIN_WITH_PERIODIC_SNOW = "RAIN_WITH_PERIODIC_SNOW"
        SNOWRAIN_MIX_LATER_BECOMING_CLEAR_SNOW_AS_MAIN = "SNOWRAIN_MIX_LATER_BECOMING_CLEAR_SNOW_AS_MAIN"
        SNOWRAIN_MIX_LATER_BECOMING_CLOUDY_SNOW_AS_MAIN = "SNOWRAIN_MIX_LATER_BECOMING_CLOUDY_SNOW_AS_MAIN"
        SNOWRAIN_MIX_SNOW_AS_MAIN = "SNOWRAIN_MIX_SNOW_AS_MAIN"
        SNOW_ACCOMPANIED_BY_LIGHTNING = "SNOW_ACCOMPANIED_BY_LIGHTNING"
        SNOW_BECOMING_SLEET = "SNOW_BECOMING_SLEET"
        SNOW_LATER_CLEAR = "SNOW_LATER_CLEAR"
        SNOW_LATER_CLOUDY = "SNOW_LATER_CLOUDY"
        SNOW_LATER_RAIN = "SNOW_LATER_RAIN"
        SNOW_PERIODICALLY_CLEAR = "SNOW_PERIODICALLY_CLEAR"
        SNOW_THAT_PERIODICALLY_STOPS = "SNOW_THAT_PERIODICALLY_STOPS"
        SNOW_TURNING_TO_RAIN_AROUND_NOON = "SNOW_TURNING_TO_RAIN_AROUND_NOON"
        SNOW_TURNING_TO_RAIN_IN_THE_EVENING = "SNOW_TURNING_TO_RAIN_IN_THE_EVENING"
        SNOW_TURNING_TO_RAIN_IN_THE_NIGHT = "SNOW_TURNING_TO_RAIN_IN_THE_NIGHT"
        SNOW_WITH_BRIEF_RAIN = "SNOW_WITH_BRIEF_RAIN"
        SNOW_WITH_BRIEF_SLEET = "SNOW_WITH_BRIEF_SLEET"
        SNOW_WITH_PERIODIC_RAIN = "SNOW_WITH_PERIODIC_RAIN"
        VERY_HOT = "VERY_HOT"
        SLEET = "SLEET"
        HEAVY_RAIN_TO_RAINSTORM = "HEAVY_RAIN_TO_RAINSTORM"

    icon_base_uri: str = field(metadata={"alias": "iconBaseUri"})
    """The base URI for the icon not including the file type extension."""

    description: LocalizedText
    """The textual description for this weather condition (localized)."""

    type: Type
    """The type of weather condition."""


@dataclass
class IceThickness(BaseModel):
    """Represents ice thickness conditions."""

    class Unit(ApiStrEnum):
        """Represents the unit used to measure the ice thickness."""

        UNIT_UNSPECIFIED = "UNIT_UNSPECIFIED"
        MILLIMETERS = "MILLIMETERS"
        INCHES = "INCHES"

    thickness: float | None = None
    """The ice thickness value."""

    unit: Unit = Unit.UNIT_UNSPECIFIED
    """The code that represents the unit used to measure the ice thickness."""


@dataclass
class CurrentConditionsHistory(BaseModel):
    """Represents a set of changes in the current conditions over the last 24 hours."""

    temperature_change: Temperature = field(metadata={"alias": "temperatureChange"})
    """The current temperature minus the temperature 24 hours ago."""

    max_temperature: Temperature = field(metadata={"alias": "maxTemperature"})
    """The maximum (high) temperature in the past 24 hours."""

    min_temperature: Temperature = field(metadata={"alias": "minTemperature"})
    """The minimum (low) temperature in the past 24 hours."""

    qpf: QuantitativePrecipitationForecast
    """The amount of precipitation (rain or snow) accumulated over the last 24 hours."""

    snow_qpf: QuantitativePrecipitationForecast | None = field(default=None, metadata={"alias": "snowQpf"})
    """The amount of snow accumulation over the last 24 hours, measured as liquid water equivalent."""


@dataclass
class CurrentConditionsResponse(BaseModel):
    """Response model for the currentConditions.lookup method."""

    current_time: str = field(metadata={"alias": "currentTime"})
    """Current time (UTC) associated with the returned data."""

    time_zone: TimeZone = field(metadata={"alias": "timeZone"})
    """The time zone at the requested location."""

    weather_condition: WeatherCondition = field(metadata={"alias": "weatherCondition"})
    """The current weather condition."""

    temperature: Temperature
    """The current temperature."""

    feels_like_temperature: Temperature = field(metadata={"alias": "feelsLikeTemperature"})
    """The measure of how the temperature currently feels like."""

    dew_point: Temperature = field(metadata={"alias": "dewPoint"})
    """The current dew point temperature."""

    heat_index: Temperature = field(metadata={"alias": "heatIndex"})
    """The current heat index temperature."""

    wind_chill: Temperature = field(metadata={"alias": "windChill"})
    """The current wind chill, air temperature exposed on the skin."""

    precipitation: Precipitation
    """Current precipitation probability and accumulated amount over the last hour."""

    air_pressure: AirPressure = field(metadata={"alias": "airPressure"})
    """The current air pressure conditions."""

    wind: Wind
    """The current wind conditions."""

    visibility: Visibility
    """The current visibility."""

    current_conditions_history: CurrentConditionsHistory = field(metadata={"alias": "currentConditionsHistory"})
    """The changes in the current conditions over the last 24 hours."""

    is_daytime: bool = field(metadata={"alias": "isDaytime"})
    """True if the current time is between local sunrise (inclusive) and sunset."""

    relative_humidity: int = field(metadata={"alias": "relativeHumidity"})
    """The current percent of relative humidity (0-100)."""

    uv_index: int = field(metadata={"alias": "uvIndex"})
    """The current ultraviolet (UV) index."""

    thunderstorm_probability: int | None = field(default=None, metadata={"alias": "thunderstormProbability"})
    """The current thunderstorm probability (0-100). Omitted in some regions (e.g. Japan and South Korea)."""

    cloud_cover: int | None = field(default=None, metadata={"alias": "cloudCover"})
    """The current percentage of the sky covered by clouds (0-100). Omitted in some regions (e.g. Japan and South Korea)."""


@dataclass
class Date(BaseModel):
    """Represents a whole or partial calendar date."""

    year: int
    """Year of the date. Must be from 1 to 9999, or 0."""

    month: int
    """Month of a year. Must be from 1 to 12, or 0."""

    day: int
    """Day of a month. Must be from 1 to 31, or 0."""


@dataclass
class ForecastDayPart(BaseModel):
    """Represents a forecast record for a part of the day (daytime, nighttime, or full day)."""

    interval: Interval
    """The UTC date and time when this part of the day starts and ends."""

    weather_condition: WeatherCondition = field(metadata={"alias": "weatherCondition"})
    """The forecasted weather condition."""

    precipitation: Precipitation
    """The forecasted precipitation."""

    wind: Wind
    """The average wind direction and maximum speed and gust."""

    relative_humidity: int = field(metadata={"alias": "relativeHumidity"})
    """The forecasted percent of relative humidity (0-100)."""

    uv_index: int = field(metadata={"alias": "uvIndex"})
    """The maximum forecasted ultraviolet (UV) index."""

    thunderstorm_probability: int | None = field(default=None, metadata={"alias": "thunderstormProbability"})
    """The average thunderstorm probability. Omitted in some regions (e.g. Japan and South Korea)."""

    cloud_cover: int | None = field(default=None, metadata={"alias": "cloudCover"})
    """Average cloud cover percent. Omitted in some regions (e.g. Japan and South Korea)."""

    ice_thickness: IceThickness | None = field(default=None, metadata={"alias": "iceThickness"})
    """The forecasted ice thickness."""


@dataclass
class SunEvents(BaseModel):
    """Represents the events related to the sun (e.g. sunrise, sunset)."""

    sunrise_time: str | None = field(default=None, metadata={"alias": "sunriseTime"})
    """The time when the sun rises. Unset in polar regions."""

    sunset_time: str | None = field(default=None, metadata={"alias": "sunsetTime"})
    """The time when the sun sets. Unset in polar regions."""


@dataclass
class MoonEvents(BaseModel):
    """Represents the events related to the moon (e.g. moonrise, moonset)."""

    class MoonPhase(ApiStrEnum):
        """Marks the moon phase (a.k.a. lunar phase)."""

        PHASE_UNSPECIFIED = "PHASE_UNSPECIFIED"
        NEW_MOON = "NEW_MOON"
        WAXING_CRESCENT = "WAXING_CRESCENT"
        FIRST_QUARTER = "FIRST_QUARTER"
        WAXING_GIBBOUS = "WAXING_GIBBOUS"
        FULL_MOON = "FULL_MOON"
        WANING_GIBBOUS = "WANING_GIBBOUS"
        LAST_QUARTER = "LAST_QUARTER"
        WANING_CRESCENT = "WANING_CRESCENT"

    moon_phase: MoonPhase = field(metadata={"alias": "moonPhase"})
    """The moon phase (a.k.a. lunar phase)."""

    moonrise_times: list[str] = field(default_factory=list, metadata={"alias": "moonriseTimes"})
    """The time(s) when the upper limb of the moon appears above the horizon."""

    moonset_times: list[str] = field(default_factory=list, metadata={"alias": "moonsetTimes"})
    """The time(s) when the upper limb of the moon disappears below the horizon."""


@dataclass
class ForecastDay(BaseModel):
    """Represents a daily forecast record at a given location."""

    interval: Interval
    """The UTC time interval when this forecasted day starts and ends."""

    display_date: Date = field(metadata={"alias": "displayDate"})
    """The local date in the time zone of the location."""

    max_temperature: Temperature = field(metadata={"alias": "maxTemperature"})
    """The maximum (high) temperature throughout the day."""

    min_temperature: Temperature = field(metadata={"alias": "minTemperature"})
    """The minimum (low) temperature throughout the day."""

    feels_like_max_temperature: Temperature = field(metadata={"alias": "feelsLikeMaxTemperature"})
    """The maximum (high) feels-like temperature throughout the day."""

    feels_like_min_temperature: Temperature = field(metadata={"alias": "feelsLikeMinTemperature"})
    """The minimum (low) feels-like temperature throughout the day."""

    max_heat_index: Temperature = field(metadata={"alias": "maxHeatIndex"})
    """The maximum heat index temperature throughout the day."""

    sun_events: SunEvents = field(metadata={"alias": "sunEvents"})
    """The events related to the sun (e.g. sunrise, sunset)."""

    moon_events: MoonEvents = field(metadata={"alias": "moonEvents"})
    """The events related to the moon (e.g. moonrise, moonset)."""

    daytime_forecast: ForecastDayPart | None = field(default=None, metadata={"alias": "daytimeForecast"})
    """The forecasted weather conditions for the daytime part of the day."""

    nighttime_forecast: ForecastDayPart | None = field(default=None, metadata={"alias": "nighttimeForecast"})
    """The forecasted weather conditions for the nighttime part of the day."""

    full_day_forecast: ForecastDayPart | None = field(default=None, metadata={"alias": "fullDayForecast"})
    """The forecasted weather conditions for the full day (returned instead of daytime/nighttime in Japan and South Korea)."""

    ice_thickness: IceThickness | None = field(default=None, metadata={"alias": "iceThickness"})
    """The accumulated amount of ice throughout the entire day."""


@dataclass
class DailyForecastResponse(BaseModel):
    """Response model for the forecast.days.lookup method."""

    time_zone: TimeZone = field(metadata={"alias": "timeZone"})
    """The time zone at the requested location."""

    forecast_days: list[ForecastDay] = field(default_factory=list, metadata={"alias": "forecastDays"})
    """The daily forecast records."""

    next_page_token: str | None = field(default=None, metadata={"alias": "nextPageToken"})
    """The token to retrieve the next page."""


@dataclass
class DateTime(BaseModel):
    """Represents civil time (or occasionally physical time)."""

    year: int | None = None
    """Optional. Year of date. Must be from 1 to 9999, or 0."""

    month: int | None = None
    """Optional. Month of year. Must be from 1 to 12, or 0."""

    day: int | None = None
    """Optional. Day of month. Must be from 1 to 31, or 0."""

    hours: int | None = None
    """Optional. Hours of day in 24 hour format. Should be from 0 to 23."""

    minutes: int | None = None
    """Optional. Minutes of hour of day. Must be from 0 to 59."""

    seconds: int | None = None
    """Optional. Seconds of minutes of the time. Must normally be from 0 to 59."""

    nanos: int | None = None
    """Optional. Fractions of seconds in nanoseconds."""

    utc_offset: str | None = field(default=None, metadata={"alias": "utcOffset"})
    """Optional. UTC offset. Must be whole seconds, between -18 and +18 hours."""

    time_zone: TimeZone | None = field(default=None, metadata={"alias": "timeZone"})
    """Optional. Time zone."""


@dataclass
class ForecastHour(BaseModel):
    """Represents an hourly forecast record at a given location."""

    interval: Interval
    """The one hour interval (in UTC time) this forecast data is valid for."""

    display_date_time: DateTime = field(metadata={"alias": "displayDateTime"})
    """The local date and time in the time zone of the location."""

    weather_condition: WeatherCondition = field(metadata={"alias": "weatherCondition"})
    """The forecasted weather condition."""

    temperature: Temperature
    """The forecasted temperature."""

    feels_like_temperature: Temperature = field(metadata={"alias": "feelsLikeTemperature"})
    """The measure of how the temperature will feel like."""

    dew_point: Temperature = field(metadata={"alias": "dewPoint"})
    """The forecasted dew point temperature."""

    heat_index: Temperature = field(metadata={"alias": "heatIndex"})
    """The forecasted heat index temperature."""

    wind_chill: Temperature = field(metadata={"alias": "windChill"})
    """The forecasted wind chill, air temperature exposed on the skin."""

    wet_bulb_temperature: Temperature = field(metadata={"alias": "wetBulbTemperature"})
    """The forecasted wet bulb temperature, lowest temperature achievable by evaporating water."""

    precipitation: Precipitation
    """The forecasted precipitation probability and amount over the last hour."""

    air_pressure: AirPressure = field(metadata={"alias": "airPressure"})
    """The forecasted air pressure conditions."""

    wind: Wind
    """The forecasted wind conditions."""

    visibility: Visibility
    """The forecasted visibility."""

    is_daytime: bool = field(metadata={"alias": "isDaytime"})
    """True if this hour is between the local sunrise (inclusive) and sunset."""

    relative_humidity: int = field(metadata={"alias": "relativeHumidity"})
    """The forecasted percent of relative humidity (0-100)."""

    uv_index: int = field(metadata={"alias": "uvIndex"})
    """The forecasted ultraviolet (UV) index."""

    thunderstorm_probability: int | None = field(default=None, metadata={"alias": "thunderstormProbability"})
    """The forecasted thunderstorm probability (0-100). Omitted in some regions (e.g. Japan and South Korea)."""

    cloud_cover: int | None = field(default=None, metadata={"alias": "cloudCover"})
    """The forecasted percentage of the sky covered by clouds (0-100). Omitted in some regions (e.g. Japan and South Korea)."""

    ice_thickness: IceThickness | None = field(default=None, metadata={"alias": "iceThickness"})
    """The forecasted ice thickness."""


@dataclass
class HourlyForecastResponse(BaseModel):
    """Response model for the forecast.hours.lookup method."""

    time_zone: TimeZone = field(metadata={"alias": "timeZone"})
    """The time zone at the requested location."""

    forecast_hours: list[ForecastHour] = field(default_factory=list, metadata={"alias": "forecastHours"})
    """The hourly forecast records."""

    next_page_token: str | None = field(default=None, metadata={"alias": "nextPageToken"})
    """The token to retrieve the next page."""


@dataclass
class PrecipitationSegment(BaseModel):
    """Represents a segment of precipitation forecast data."""

    class DominantPrecipitationType(ApiStrEnum):
        """Represents the type of precipitation of a segment."""

        DOMINANT_PRECIPITATION_TYPE_UNSPECIFIED = "DOMINANT_PRECIPITATION_TYPE_UNSPECIFIED"
        NONE = "NONE"
        RAIN = "RAIN"
        SNOW = "SNOW"
        HAIL = "HAIL"

    class PrecipitationIntensity(ApiStrEnum):
        """Represents the precipitation intensity of a segment."""

        PRECIPITATION_INTENSITY_UNSPECIFIED = "PRECIPITATION_INTENSITY_UNSPECIFIED"
        NO_INTENSITY = "NO_INTENSITY"
        LIGHT = "LIGHT"
        MID_LIGHT = "MID_LIGHT"
        MODERATE = "MODERATE"
        MID_MODERATE = "MID_MODERATE"
        HEAVY = "HEAVY"
        MID_HEAVY = "MID_HEAVY"

    time_frame: Interval = field(metadata={"alias": "timeFrame"})
    """The timeframe relevant to the segment."""

    type: DominantPrecipitationType = DominantPrecipitationType.DOMINANT_PRECIPITATION_TYPE_UNSPECIFIED
    """A code that indicates the type of precipitation."""

    probability: int = 0
    """The chance of precipitation (values from 0 to 100)."""

    qpf: QuantitativePrecipitationForecast | None = None
    """The amount of precipitation, measured as liquid water equivalent."""

    snowfall_amount: QuantitativePrecipitationForecast | None = field(default=None, metadata={"alias": "snowfallAmount"})
    """The amount of snow accumulation, measured as liquid water equivalent."""

    intensity: PrecipitationIntensity = PrecipitationIntensity.PRECIPITATION_INTENSITY_UNSPECIFIED
    """A code that indicates the precipitation intensity of the segment."""


@dataclass
class MinuteForecastResponse(BaseModel):
    """Response model for the forecast.minutes.lookup method."""

    overall_prediction_timeframe: Interval = field(metadata={"alias": "overallPredictionTimeframe"})
    """The overall timeframe for the predictions."""

    time_zone: TimeZone = field(metadata={"alias": "timeZone"})
    """The time zone at the requested location."""

    segments: list[PrecipitationSegment] = field(default_factory=list)
    """The minute-level prediction segments."""

    next_page_token: str | None = field(default=None, metadata={"alias": "nextPageToken"})
    """The token to retrieve the next page."""
