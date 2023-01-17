class Weather:
    def __init__(self, lid, location,humidity,rain,temperature,wind_speed,feels_like,json):
        self.lid = lid
        self.location = location
        self.humidity = humidity
        self.rain = rain
        self.temperature = temperature
        self.wind_speed = wind_speed
        self.feels_like = feels_like
        self.json = json
