"""Models for the Google Weather API."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class AirPressure(DataClassJSONMixin):
    """Represents the atmospheric air pressure conditions."""

    mean_sea_level_millibars: float = field(metadata={"alias": "meanSeaLevelMillibars"})
    """The mean sea level air pressure in millibars."""


@dataclass
class Interval(DataClassJSONMixin):
    """Represents a time interval."""

    start_time: str = field(metadata={"alias": "startTime"})
    """Inclusive start of the interval in RFC 3339 format."""

    end_time: str | None = field(default=None, metadata={"alias": "endTime"})
    """Optional. Exclusive end of the interval in RFC 3339 format."""


@dataclass
class TimeZone(DataClassJSONMixin):
    """Represents a time zone from the IANA Time Zone Database."""

    id: str
    """IANA Time Zone Database time zone. For example "America/New_York"."""

    version: str | None = None
    """Optional. IANA Time Zone Database version number. For example "2019a"."""


@dataclass
class LocalizedText(DataClassJSONMixin):
    """Localized variant of a text in a particular language."""

    text: str
    """Localized string in the language corresponding to languageCode below."""

    language_code: str = field(metadata={"alias": "languageCode"})
    """The text's BCP-47 language code, such as "en-US" or "sr-Latn"."""


@dataclass
class Temperature(DataClassJSONMixin):
    """Represents a temperature value."""

    class TemperatureUnit(StrEnum):
        """Represents a unit used to measure temperatures."""

        TEMPERATURE_UNIT_UNSPECIFIED = "TEMPERATURE_UNIT_UNSPECIFIED"
        CELSIUS = "CELSIUS"
        FAHRENHEIT = "FAHRENHEIT"

    degrees: float
    """The temperature value (in degrees) in the specified unit."""

    unit: TemperatureUnit
    """The code for the unit used to measure the temperature value."""


@dataclass
class QuantitativePrecipitationForecast(DataClassJSONMixin):
    """Represents the expected amount of melted precipitation."""

    class Unit(StrEnum):
        """Represents the unit used to measure the amount of accumulated precipitation."""

        UNIT_UNSPECIFIED = "UNIT_UNSPECIFIED"
        MILLIMETERS = "MILLIMETERS"
        INCHES = "INCHES"

    quantity: float
    """The amount of precipitation, measured as liquid water equivalent."""

    unit: Unit
    """The code of the unit used to measure the amount of accumulated precipitation."""


@dataclass
class PrecipitationProbability(DataClassJSONMixin):
    """Represents the probability of precipitation at a given location."""

    class PrecipitationType(StrEnum):
        """Represents the type of precipitation at a given location."""

        PRECIPITATION_TYPE_UNSPECIFIED = "PRECIPITATION_TYPE_UNSPECIFIED"
        NONE = "NONE"
        SNOW = "SNOW"
        RAIN = "RAIN"
        LIGHT_RAIN = "LIGHT_RAIN"
        HEAVY_RAIN = "HEAVY_RAIN"
        RAIN_AND_SNOW = "RAIN_AND_SNOW"
        SLEET = "SLEET"
        FREEZING_RAIN = "FREEZING_RAIN"

    type: PrecipitationType
    """A code that indicates the type of precipitation."""

    percent: int
    """A percentage from 0 to 100 that indicates the chances of precipitation."""


@dataclass
class Precipitation(DataClassJSONMixin):
    """Represents a set of precipitation values at a given location."""

    probability: PrecipitationProbability
    """The probability of precipitation (values from 0 to 100)."""

    qpf: QuantitativePrecipitationForecast
    """The amount of precipitation (rain or snow), measured as liquid water."""

    snow_qpf: QuantitativePrecipitationForecast | None = field(
        default=None, metadata={"alias": "snowQpf"}
    )
    """The amount of snow accumulation, measured as liquid water equivalent."""


@dataclass
class WindSpeed(DataClassJSONMixin):
    """Represents the speed of the wind."""

    class SpeedUnit(StrEnum):
        """Represents the unit used to measure speed."""

        SPEED_UNIT_UNSPECIFIED = "SPEED_UNIT_UNSPECIFIED"
        KILOMETERS_PER_HOUR = "KILOMETERS_PER_HOUR"
        MILES_PER_HOUR = "MILES_PER_HOUR"

    value: float
    """The value of the wind speed."""

    unit: SpeedUnit
    """The code that represents the unit used to measure the wind speed."""


@dataclass
class WindDirection(DataClassJSONMixin):
    """Represents the direction from which the wind originates."""

    class CardinalDirection(StrEnum):
        """Represents a cardinal direction (including ordinal directions)."""

        CARDINAL_DIRECTION_UNSPECIFIED = "CARDINAL_DIRECTION_UNSPECIFIED"
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
class Wind(DataClassJSONMixin):
    """Represents a set of wind properties."""

    direction: WindDirection
    """The direction of the wind, the angle it is coming from."""

    speed: WindSpeed
    """The speed of the wind."""

    gust: WindSpeed
    """The wind gust (sudden increase in the wind speed)."""


@dataclass
class Visibility(DataClassJSONMixin):
    """Represents visibility conditions, the distance at which objects can be discerned."""

    class Unit(StrEnum):
        """Represents the unit used to measure the visibility distance."""

        UNIT_UNSPECIFIED = "UNIT_UNSPECIFIED"
        KILOMETERS = "KILOMETERS"
        MILES = "MILES"

    distance: float
    """The visibility distance in the specified unit."""

    unit: Unit
    """The code that represents the unit used to measure the distance."""


@dataclass
class WeatherCondition(DataClassJSONMixin):
    """Represents a weather condition for a given location at a given period of time."""

    class Type(StrEnum):
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

    icon_base_uri: str = field(metadata={"alias": "iconBaseUri"})
    """The base URI for the icon not including the file type extension."""

    description: LocalizedText
    """The textual description for this weather condition (localized)."""

    type: Type
    """The type of weather condition."""


@dataclass
class IceThickness(DataClassJSONMixin):
    """Represents ice thickness conditions."""

    class Unit(StrEnum):
        """Represents the unit used to measure the ice thickness."""

        UNIT_UNSPECIFIED = "UNIT_UNSPECIFIED"
        MILLIMETERS = "MILLIMETERS"
        INCHES = "INCHES"

    thickness: float
    """The ice thickness value."""

    unit: Unit
    """The code that represents the unit used to measure the ice thickness."""


@dataclass
class CurrentConditionsHistory(DataClassJSONMixin):
    """Represents a set of changes in the current conditions over the last 24 hours."""

    temperature_change: Temperature = field(metadata={"alias": "temperatureChange"})
    """The current temperature minus the temperature 24 hours ago."""

    max_temperature: Temperature = field(metadata={"alias": "maxTemperature"})
    """The maximum (high) temperature in the past 24 hours."""

    min_temperature: Temperature = field(metadata={"alias": "minTemperature"})
    """The minimum (low) temperature in the past 24 hours."""

    qpf: QuantitativePrecipitationForecast
    """The amount of precipitation (rain or snow) accumulated over the last 24 hours."""


@dataclass
class CurrentConditionsResponse(DataClassJSONMixin):
    """Response model for the currentConditions.lookup method."""

    current_time: str = field(metadata={"alias": "currentTime"})
    """Current time (UTC) associated with the returned data."""

    time_zone: TimeZone = field(metadata={"alias": "timeZone"})
    """The time zone at the requested location."""

    weather_condition: WeatherCondition = field(metadata={"alias": "weatherCondition"})
    """The current weather condition."""

    temperature: Temperature
    """The current temperature."""

    feels_like_temperature: Temperature = field(
        metadata={"alias": "feelsLikeTemperature"}
    )
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

    current_conditions_history: CurrentConditionsHistory = field(
        metadata={"alias": "currentConditionsHistory"}
    )
    """The changes in the current conditions over the last 24 hours."""

    is_daytime: bool = field(metadata={"alias": "isDaytime"})
    """True if the current time is between local sunrise (inclusive) and sunset."""

    relative_humidity: int = field(metadata={"alias": "relativeHumidity"})
    """The current percent of relative humidity (0-100)."""

    uv_index: int = field(metadata={"alias": "uvIndex"})
    """The current ultraviolet (UV) index."""

    thunderstorm_probability: int = field(metadata={"alias": "thunderstormProbability"})
    """The current thunderstorm probability (0-100)."""

    cloud_cover: int = field(metadata={"alias": "cloudCover"})
    """The current percentage of the sky covered by clouds (0-100)."""


@dataclass
class Date(DataClassJSONMixin):
    """Represents a whole or partial calendar date."""

    year: int
    """Year of the date. Must be from 1 to 9999, or 0."""

    month: int
    """Month of a year. Must be from 1 to 12, or 0."""

    day: int
    """Day of a month. Must be from 1 to 31, or 0."""


@dataclass
class ForecastDayPart(DataClassJSONMixin):
    """Represents a forecast record for a part of the day (daytime or nighttime)."""

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

    thunderstorm_probability: int = field(metadata={"alias": "thunderstormProbability"})
    """The average thunderstorm probability."""

    cloud_cover: int = field(metadata={"alias": "cloudCover"})
    """Average cloud cover percent."""

    ice_thickness: IceThickness | None = field(
        default=None, metadata={"alias": "iceThickness"}
    )
    """The forecasted ice thickness."""


@dataclass
class SunEvents(DataClassJSONMixin):
    """Represents the events related to the sun (e.g. sunrise, sunset)."""

    sunrise_time: str | None = field(default=None, metadata={"alias": "sunriseTime"})
    """The time when the sun rises. Unset in polar regions."""

    sunset_time: str | None = field(default=None, metadata={"alias": "sunsetTime"})
    """The time when the sun sets. Unset in polar regions."""


@dataclass
class MoonEvents(DataClassJSONMixin):
    """Represents the events related to the moon (e.g. moonrise, moonset)."""

    class MoonPhase(StrEnum):
        """Marks the moon phase (a.k.a. lunar phase)."""

        MOON_PHASE_UNSPECIFIED = "MOON_PHASE_UNSPECIFIED"
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

    moonrise_times: list[str] = field(
        default_factory=list, metadata={"alias": "moonriseTimes"}
    )
    """The time(s) when the upper limb of the moon appears above the horizon."""

    moonset_times: list[str] = field(
        default_factory=list, metadata={"alias": "moonsetTimes"}
    )
    """The time(s) when the upper limb of the moon disappears below the horizon."""


@dataclass
class ForecastDay(DataClassJSONMixin):
    """Represents a daily forecast record at a given location."""

    interval: Interval
    """The UTC time interval when this forecasted day starts and ends."""

    display_date: Date = field(metadata={"alias": "displayDate"})
    """The local date in the time zone of the location."""

    daytime_forecast: ForecastDayPart = field(metadata={"alias": "daytimeForecast"})
    """The forecasted weather conditions for the daytime part of the day."""

    nighttime_forecast: ForecastDayPart = field(metadata={"alias": "nighttimeForecast"})
    """The forecasted weather conditions for the nighttime part of the day."""

    max_temperature: Temperature = field(metadata={"alias": "maxTemperature"})
    """The maximum (high) temperature throughout the day."""

    min_temperature: Temperature = field(metadata={"alias": "minTemperature"})
    """The minimum (low) temperature throughout the day."""

    feels_like_max_temperature: Temperature = field(
        metadata={"alias": "feelsLikeMaxTemperature"}
    )
    """The maximum (high) feels-like temperature throughout the day."""

    feels_like_min_temperature: Temperature = field(
        metadata={"alias": "feelsLikeMinTemperature"}
    )
    """The minimum (low) feels-like temperature throughout the day."""

    max_heat_index: Temperature = field(metadata={"alias": "maxHeatIndex"})
    """The maximum heat index temperature throughout the day."""

    sun_events: SunEvents = field(metadata={"alias": "sunEvents"})
    """The events related to the sun (e.g. sunrise, sunset)."""

    moon_events: MoonEvents = field(metadata={"alias": "moonEvents"})
    """The events related to the moon (e.g. moonrise, moonset)."""

    ice_thickness: IceThickness | None = field(
        default=None, metadata={"alias": "iceThickness"}
    )
    """The accumulated amount of ice throughout the entire day."""


@dataclass
class DailyForecastResponse(DataClassJSONMixin):
    """Response model for the forecast.days.lookup method."""

    forecast_days: list[ForecastDay] = field(metadata={"alias": "forecastDays"})
    """The daily forecast records."""

    time_zone: TimeZone = field(metadata={"alias": "timeZone"})
    """The time zone at the requested location."""

    next_page_token: str | None = field(
        default=None, metadata={"alias": "nextPageToken"}
    )
    """The token to retrieve the next page."""


@dataclass
class DateTime(DataClassJSONMixin):
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
class ForecastHour(DataClassJSONMixin):
    """Represents an hourly forecast record at a given location."""

    interval: Interval
    """The one hour interval (in UTC time) this forecast data is valid for."""

    display_date_time: DateTime = field(metadata={"alias": "displayDateTime"})
    """The local date and time in the time zone of the location."""

    weather_condition: WeatherCondition = field(metadata={"alias": "weatherCondition"})
    """The forecasted weather condition."""

    temperature: Temperature
    """The forecasted temperature."""

    feels_like_temperature: Temperature = field(
        metadata={"alias": "feelsLikeTemperature"}
    )
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

    thunderstorm_probability: int = field(metadata={"alias": "thunderstormProbability"})
    """The forecasted thunderstorm probability (0-100)."""

    cloud_cover: int = field(metadata={"alias": "cloudCover"})
    """The forecasted percentage of the sky covered by clouds (0-100)."""

    ice_thickness: IceThickness | None = field(
        default=None, metadata={"alias": "iceThickness"}
    )
    """The forecasted ice thickness."""


@dataclass
class HourlyForecastResponse(DataClassJSONMixin):
    """Response model for the forecast.hours.lookup method."""

    forecast_hours: list[ForecastHour] = field(metadata={"alias": "forecastHours"})
    """The hourly forecast records."""

    time_zone: TimeZone = field(metadata={"alias": "timeZone"})
    """The time zone at the requested location."""

    next_page_token: str | None = field(
        default=None, metadata={"alias": "nextPageToken"}
    )
    """The token to retrieve the next page."""
