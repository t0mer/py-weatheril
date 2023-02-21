from typing import Dict
from json import JSONEncoder
from datetime import datetime


class Forecast:
    def __init__(self,days: list = []):
        self.days = days


class Daily:
    def __init__(self, date: datetime, location: str, day: str,weather: str,weather_code: str, minimum_temperature: int, maximum_temperature: int, maximum_uvi: int, description: str, hours: list = []) -> None:
        self.date = date
        self.location = location
        self.day = day
        self.weather = weather
        self.weather_code = weather_code
        self.minimum_temperature = minimum_temperature
        self.maximum_temperature = maximum_temperature
        self.maximum_uvi = maximum_uvi
        self.description = description
        self.hours = hours



class Hourly:
    def __init__(self,hour: str,forecast_time: datetime,weather: str,weather_code: str, temperature: int,heat_stress:int,relative_humidity: int,rain: float, wind_speed:int, wind_direction:str ) -> None:
        self.hour = hour
        self.forecast_time = forecast_time
        self.weather = weather
        self.temperature = temperature
        self.weather_code = weather_code
        self.heat_stress = heat_stress
        self.relative_humidity = relative_humidity
        self.rain = rain
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction




class ForecastEncoder(JSONEncoder):
    """
    Return Contact object as json
    """
    def default(self, o):
        return o.__dict__
