from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from json import JSONEncoder
from typing import Optional

from .utils import (
    get_location_name_by_id,
    get_day_of_the_week,
    get_weather_description_by_code,
    get_wind_direction,
)


@dataclass
class Forecast:
    days: list[Daily] = field(default_factory=list)


@dataclass
class Daily:
    language: str
    date: datetime
    lid: str
    weather_code: Optional[int]
    minimum_temperature: int
    maximum_temperature: int
    maximum_uvi: int
    u_v_i_factor: float
    description: str
    hours: list[Hourly] = field(default_factory=list)
    day: str = field(init=False)
    location: str = field(init=False)
    weather: str = field(init=False)

    def __post_init__(self):
        self.day = get_day_of_the_week(self.language, self.date)
        self.location = get_location_name_by_id(self.language, self.lid)
        self.weather = get_weather_description_by_code(self.language, self.weather_code)


@dataclass
class Hourly:
    language: str
    hour: str
    forecast_time: datetime
    created: datetime
    temperature: Optional[int]
    precise_temperature: Optional[float]
    weather_code: Optional[int]
    heat_stress: Optional[float]
    heat_stress_level: Optional[int]
    pm10: Optional[int]
    relative_humidity: Optional[int]
    rain: Optional[float]
    rain_chance: Optional[float]
    wind_speed: Optional[int]
    wind_direction_id: Optional[int]
    wind_chill: Optional[int]
    weather: str = field(init=False)
    wind_direction: str = field(init=False)
    wave_height: Optional[float]
    u_v_index: Optional[int]
    u_v_i_max: Optional[int]
    gust_speed: Optional[int]

    def __post_init__(self):
        self.weather = get_weather_description_by_code(self.language, self.weather_code)
        self.wind_direction = get_wind_direction(self.language, self.wind_direction_id)


class ForecastEncoder(JSONEncoder):
    """
    Return Contact object as json
    """

    def default(self, o):
        return o.__dict__
