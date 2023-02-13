class Weather:
    def __init__(self, lid, location,humidity,rain,temperature,wind_speed,feels_like,forecast_time,u_v_index,json,weather_code,description):
        self.lid = lid
        self.location = location
        self.humidity = humidity
        self.rain = rain
        self.temperature = temperature
        self.wind_speed = wind_speed
        self.feels_like = feels_like
        self.u_v_index = u_v_index
        self.forecast_time = forecast_time
        self.json = json
        self.weather_code = weather_code
        self.description = description
