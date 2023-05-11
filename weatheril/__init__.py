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


def _get_value(data: dict, key: str, dict_key: str, default_value: str = None):
    """
        Get default value from nested dictionary
    :param data: dictionary
    :param key: first level key
    :param dict_key: second level key
    :param default_value: default value
    :return: data[key][dict_key] or default_value
    """
    if key in data and dict_key in data.get(key):
        return data.get(key).get(dict_key) or default_value
    else:
        return default_value


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
                                  lid=weather_data.get("lid"),
                                  humidity=int(weather_data.get("relative_humidity", "0") or "0"),
                                  rain=float(weather_data.get("rain", "0.0") or "0.0"),
                                  temperature=int(weather_data.get("temperature", "0") or "0"),
                                  wind_speed=int(weather_data.get("wind_speed", "0") or "0"),
                                  feels_like=int(weather_data.get("feels_like", "0") or "0"),
                                  u_v_index=int(weather_data.get("u_v_index", "0") or "0"),
                                  forecast_time=datetime.strptime(weather_data.get("forecast_time"), '%Y-%m-%d %H:%M:%S'),
                                  json=weather_data,
                                  weather_code=weather_data.get("weather_code", "-1" or "-1")
                                  )
            else:
                logger.error('No "' + self.location + '" in current analysis response')
                logger.debug('Response: ' + data)
                return None
        except Exception as e:
            logger.error('Error getting current analysis.')
            logger.exception(e)
            return None

    def get_forecast(self):
        '''
        Get weather forecast
        return: Forecast object
        '''
        try:
            forecast_data = self.get_data(forecast_url.format(self.language, self.location))
            days = []
            if "data" not in forecast_data:
                logger.error("Error getting forecast data")
                logger.debug("Response: " + data)
                return None
            data = forecast_data.get("data")
            for key in data.keys():
                hours = self.get_hourly_forecast(_get_value(data, key, "hourly"))
                if "description" in str(data):
                    try:
                        description = data.get("data").get(key, {}).get("country").get("description")
                    except:
                        description = ""
                else:
                    description = ""
                daily = Daily(
                    language=self.language,
                    date=datetime.strptime(key, "%Y-%m-%d"),
                    lid=_get_value(data, key, "lid", "0"),
                    weather_code=_get_value(data, key, "weather_code", "0"),
                    minimum_temperature=int(_get_value(data, key, "minimum_temperature", "0")),
                    maximum_temperature=int(_get_value(data, key, "maximum_temperature", "0")),
                    maximum_uvi=int(_get_value(data, key, "maximum_uvi", "0")),
                    hours=hours,
                    description=description.rstrip()
                )
                days.append(daily)
            return Forecast(days)

        except Exception as e:
            logger.error("Error getting forecast data")
            logger.exception(e)
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
                           forecast_time=datetime.strptime(data.get(key, {}).get("forecast_time"), "%Y-%m-%d %H:%M:%S"),
                           weather_code=_get_value(data, key, "weather_code", "0"),
                           temperature=int(_get_value(data, key, "temperature", "0")),
                           heat_stress=int(_get_value(data, key, "heat_stress", "0")),
                           relative_humidity=int(_get_value(data, key, "relative_humidity", "0")),
                           rain=float(_get_value(data, key, "rain", "0.0")),
                           wind_speed=int(_get_value(data, key, "windspeed", "0")),
                           wind_direction_id=int(_get_value(data, key, "wind_direction_id", "0"))))
            return hours
        except Exception as e:
            logger.error("Error getting hourly forecast ")
            logger.exception(e)
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
