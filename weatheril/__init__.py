"""Israel Meteorological Service unofficial python api wrapper"""
import json

import requests
from loguru import logger

from .forecast import Forecast, Daily, Hourly
from .radar_satellite import RadarSatellite
from .weather import *

images_url = "https://ims.gov.il"
locations_url = "https://ims.gov.il/{}/locations_info"
forecast_url = "https://ims.gov.il/{}/full_forecast_data/{}"
radar_url = "https://ims.gov.il/{}/radar_satellite"
current_analysis_url = "https://ims.gov.il/{}/now_analysis/{}"
weather_codes_url = "https://ims.gov.il/{}/weather_codes"

# ims.gov.il does not support ipv6 yet, `requests` use ipv6 by default
# and wait for timeout before trying ipv4, so we have to disable ipv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False


class WeatherIL:
    def __init__(self, location, language="he"):
        """
        Init the WeatherIL object.
        parameters:
            >>> location: Location Id for the forecast (Table exists in the readme)
            >>> language: can be he (Hebrew) or en (English). default will be "he"
        """
        self.language = language
        self.location = str(location)

    def get_current_analysis(self):
        try:
            logger.debug('Getting current analysis')
            data = self.get_data(current_analysis_url.format(self.language, self.location))
            if "data" in data and self.location in data.get("data"):
                weather_data = data.get("data").get(self.location)
                logger.debug('Got current analysis for location ' + str(self.location))
                return Weather(langauge=self.language,
                                  lid=int(weather_data.get("lid")),
                                  humidity=int(weather_data.get("relative_humidity")),
                                  rain=float(weather_data.get("rain")) if (weather_data.get("rain")) else 0,
                                  temperature=int(weather_data.get("temperature")),
                                  wind_speed=int(weather_data.get("wind_speed")),
                                  feels_like=int(weather_data.get("feels_like")),
                                  u_v_index=int(weather_data.get("u_v_index")),
                                  forecast_time=datetime.strptime(weather_data.get("forecast_time"), '%Y-%m-%d %H:%M:%S'),
                                  json=weather_data,
                                  weather_code=weather_data.get("weather_code")
                                  )
            else:
                logger.error('No "' + self.location + '" in current analysis response')
                logger.debug('Response: ' + data)
                return None
        except Exception as e:
            logger.error('Error getting current analysis. ' + str(e))
            return None

    def get_forecast(self):
        '''
        Get weather forecast
        return: Forecast object
        '''
        try:
            data = self.get_data(forecast_url.format(self.language, self.location))
            days = []
            if "data" not in data:
                logger.error("Error getting forecast data")
                logger.debug("Response: " + data)
                return None
            for key in data.get("data").keys():
                hours = self.get_hourly_forecast(data.get("data").get(key).get("hourly"))
                if "description" in str(data):
                    try:
                        description = data.get("data").get(key).get("country").get("description")
                    except:
                        description = ""
                else:
                    description = ""
                daily = Daily(
                    language=self.language,
                    date=datetime.strptime(key, "%Y-%m-%d"),
                    lid=data.get("data").get(key).get("daily").get("lid", "-1"),
                    weather_code=data.get("data").get(key).get("daily").get("weather_code", "0"),
                    minimum_temperature=int(data.get("data").get(key).get("daily").get("minimum_temperature", "0")),
                    maximum_temperature=int(data.get("data").get(key).get("daily").get("maximum_temperature", "0")),
                    maximum_uvi=int(data.get("data").get(key).get("daily").get("maximum_uvi", "0")),
                    hours=hours,
                    description=description.rstrip()
                )
                days.append(daily)
            return Forecast(days)

        except Exception as e:
            logger.error("Error getting forecast data " + str(e))
            return None

    def get_hourly_forecast(self, data):
        '''
        Get the hourly forecast
        '''
        hours = []
        try:
            for key in data.keys():
                hours.append(
                    Hourly(language=self.language,
                           hour=key,
                           forecast_time=datetime.strptime(data.get(key).get("forecast_time"), "%Y-%m-%d %H:%M:%S"),
                           weather_code=data.get(key).get("weather_code", "0"),
                           temperature=int(data.get(key).get("temperature", "0")),
                           heat_stress=int(data.get(key).get("heat_stress", "0")),
                           relative_humidity=int(data.get(key).get("relative_humidity", "0")),
                           rain=float(data.get("rain", "0.0")),
                           wind_speed=int(data.get(key).get("wind_speed", "0")),
                           wind_direction_id=int(data.get(key).get("wind_direction_id", "0"))))
            return hours
        except Exception as e:
            logger.error("Error getting hourly forecast" + str(e))
            return None

    def get_radar_images(self):
        '''
        Get the list of images for Satellite and Radar
        return: RadarSatellite objects with the lists
        '''
        rs = RadarSatellite()
        try:
            logger.debug('Getting radar images')
            data = self.get_data(radar_url.format(self.language))
            for key in data.get("data").get("types").get("IMSRadar"):
                rs.imsradar_images.append(images_url + key.get("file_name"))

            for key in data.get("data").get("types").get("radar"):
                rs.radar_images.append(images_url + key.get("file_name"))

            for key in data.get("data").get("types").get("MIDDLE-EAST"):
                rs.middle_east_satellite_images.append(images_url + key.get("file_name"))

            for key in data.get("data").get("types").get("EUROPE"):
                rs.europe_satellite_images.append(images_url + key.get("file_name"))

            logger.debug(f"\
                Got: {len(rs.imsradar_images)} IMS Radar Images;\
                {len(rs.radar_images)} Radar Images;\
                {len(rs.middle_east_satellite_images)} Middle East Satellite Images;\
                {len(rs.europe_satellite_images)} European Satellite Images")
            return rs
        except Exception as e:
            logger.error('Error getting images. ' + str(e))
            return rs

    def get_data(self, url):
        '''
        Helper method to get the Json data from ims website
        '''
        try:
            response = requests.get(url)
            response = json.loads(response.text)
            return response
        except Exception as e:
            logger.error('Error getting data. ' + str(e))
            return ""
