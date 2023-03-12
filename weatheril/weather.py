from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .utils import get_location_name_by_id, get_weather_description_by_code


@dataclass
class Weather:
    langauge: str
    lid: str
    humidity: int
    rain: float
    temperature: int
    wind_speed: int
    feels_like: int
    forecast_time: datetime
    u_v_index: int
    json: str
    weather_code: str
    location: str = field(init=False)
    description: str = field(init=False)

    def __post_init__(self):
        self.location = get_location_name_by_id(self.langauge, self.lid)
        self.description = get_weather_description_by_code(self.langauge, self.weather_code)

