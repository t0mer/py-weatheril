from __future__ import annotations
from typing import Dict
from json import JSONEncoder
from datetime import datetime
from utils import get_wind_direction, get_day_of_the_week, get_weather_description_by_code, get_location_name_by_id
from dataclasses import dataclass, field



@dataclass
class Forecast:
    def __init__(self,days: list = []):
        self.days = days


@dataclass
class Daily:
    def __init__(self, date: datetime, lid: str,weather: str,weather_code: str, minimum_temperature: int, maximum_temperature: int, maximum_uvi: int, description: str, hours: list = []) -> None:
        self.date = date
        self.lid = lid
        self.location = get_location_name_by_id(lid),
        self.day = get_day_of_the_week(date)
        self.weather_code = weather_code
        self.weather = get_weather_description_by_code(weather_code)
        self.minimum_temperature = minimum_temperature
        self.maximum_temperature = maximum_temperature
        self.maximum_uvi = maximum_uvi
        self.description = description
        self.hours = hours


@dataclass
class Hourly:
    def __init__(self,hour: str,forecast_time: datetime,weather_code: str, temperature: int,heat_stress:int,relative_humidity: int,rain: float, wind_speed:int, wind_direction_id:int ) -> None:
        self.hour = hour
        self.forecast_time = forecast_time
        self.temperature = temperature
        self.weather_code = weather_code
        self.weather = get_weather_description_by_code(weather_code)
        self.heat_stress = heat_stress
        self.relative_humidity = relative_humidity
        self.rain = rain
        self.wind_speed = wind_speed
        self.wind_direction_id = wind_direction_id
        self.wind_direction = get_wind_direction(self.wind_direction_id)



class ForecastEncoder(JSONEncoder):
    """
    Return Contact object as json
    """
    def default(self, o):
        return o.__dict__
