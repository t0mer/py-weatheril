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
    rain_chance: int
    temperature: float
    due_point_temp: int
    wind_speed: int
    wind_chill: int
    wind_direction_id: int
    feels_like: float
    heat_stress_level: int
    forecast_time: datetime
    u_v_index: int
    u_v_level: str
    u_v_i_max: int
    u_v_i_factor: float
    json: str
    weather_code: str
    wave_height: float
    location: str = field(init=False)
    description: str = field(init=False)

    def __post_init__(self):
        self.location = get_location_name_by_id(self.langauge, self.lid)
        self.description = get_weather_description_by_code(self.langauge, self.weather_code)

