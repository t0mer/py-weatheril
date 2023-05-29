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
city_portal_url = "https://ims.gov.il/{}/city_portal/{}"

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


def _fetch_data(url: str) -> dict:
    """
    Helper method to get the Json data from ims website
    """
    try:
        response = requests.get(url)
        response = json.loads(response.text)
        return response
    except Exception as e:
        logger.error('Error getting data. ' + str(e))
        logger.exception(e)
        return dict()


DEFAULT_CITY_PORTAL_EXPIRATION = 30


class WeatherIL:
    def __init__(self, location, language="he", city_portal_cache_expiration=DEFAULT_CITY_PORTAL_EXPIRATION):
        """
        Init the WeatherIL object.
        parameters:
            >>> location: Location Id for the forecast (Table exists in the readme)
            >>> language: can be he (Hebrew) or en (English). default will be "he"
            >>> city_portal_cache_expiration: cache expiration in days for city portal data API. default is 30 seconds
        """
        self.city_portal_cache_expiration = city_portal_cache_expiration
        self.language = language
        self.location = str(location)
        self.city_portal_data = None
        self.city_portal_last_fetch = None

    def get_current_analysis(self):
        self._get_city_portal_data()
        try:
            logger.debug('Getting current analysis')
            analysis_data = self.city_portal_data.get("analysis")
            if analysis_data:
                return Weather(langauge=self.language,
                               lid=analysis_data.get("lid"),
                               humidity=int(analysis_data.get("relative_humidity", "0") or "0"),
                               rain=float(analysis_data.get("rain", "0.0") or "0.0"),
                               rain_chance=int(analysis_data.get("rain_chance", "0") or "0"),
                               temperature=float(analysis_data.get("temperature", "0.0") or "0.0"),
                               due_point_temp=int(analysis_data.get("due_point_Temp", "0") or "0"),
                               wind_speed=int(analysis_data.get("wind_speed", "0") or "0"),
                               wind_chill=int(analysis_data.get("wind_chill", "0") or "0"),
                               wind_direction_id=int(analysis_data.get("wind_direction_id", "0") or "0"),
                               feels_like=float(analysis_data.get("feels_like", "0.0") or "0.0"),
                               heat_stress_level=int(analysis_data.get("heat_stress_level", "0") or "0"),
                               u_v_index=int(analysis_data.get("u_v_index", "0") or "0"),
                               u_v_level=analysis_data.get("u_v_level"),
                               u_v_i_max=int(analysis_data.get("u_v_i_max", "0") or "0"),
                               u_v_i_factor=float(analysis_data.get("u_v_i_factor", "0") or "0"),
                               wave_height=float(analysis_data.get("wave_height", "0.0") or "0.0"),
                               forecast_time=datetime.strptime(analysis_data.get("forecast_time"), '%Y-%m-%d %H:%M:%S'),
                               json=analysis_data,
                               weather_code=analysis_data.get("weather_code", "0")
                               )
                logger.debug('Got current analysis for location ' + str(self.location))
            else:
                logger.error('No "' + self.location + '" in current analysis response')
                logger.debug('Response: ' + analysis_data)
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
        self._get_city_portal_data()
        try:

            days = []
            forecast_data = self.city_portal_data.get("forecast_data")
            for key in forecast_data.keys():
                hours = self.get_hourly_forecast(_get_value(forecast_data, key, "hourly"))
                daily = Daily(
                    language=self.language,
                    date=datetime.strptime(key, "%Y-%m-%d"),
                    lid=_get_value(forecast_data[key], "daily", "lid", "0"),
                    weather_code=_get_value(forecast_data[key], "daily", "weather_code", "0"),
                    minimum_temperature=int(_get_value(forecast_data[key], "daily", "minimum_temperature", "0")),
                    maximum_temperature=int(_get_value(forecast_data[key], "daily", "maximum_temperature", "0")),
                    maximum_uvi=int(_get_value(forecast_data[key], "daily", "maximum_uvi", "0")),
                    hours=hours,
                    description=(_get_value(forecast_data[key], "country", "description", "")).rstrip()
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
                       precise_temperature=float(_get_value(data, key, "precise_temperature", "0.0")),
                       heat_stress=int(_get_value(data, key, "heat_stress", "0")),
                       relative_humidity=int(_get_value(data, key, "relative_humidity", "0")),
                       rain=float(_get_value(data, key, "rain", "0.0")),
                       rain_chance=int(_get_value(data, key, "rain_chance", "0")),
                       wind_speed=int(_get_value(data, key, "wind_speed", "0")),
                       wind_direction_id=int(_get_value(data, key, "wind_direction_id", "0")),
                       wave_height=float(_get_value(data, key, "wave_height", "0.0")),
                       heat_stress_level=int(_get_value(data, key, "heat_stress_level", "0")),
                       wind_chill=int(_get_value(data, key, "wind_chill", "0")),
                       u_v_index=int(_get_value(data, key, "u_v_index", "0")),
                       u_v_i_max=int(_get_value(data, key, "u_v_i_max", "0"))
                   ))
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
            data = _fetch_data(radar_url.format(self.language))
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

    def _get_city_portal_data(self) -> dict:
        """
        Get the city portal data
        return: dict
        """
        if not self.city_portal_data or (
                datetime.now() - self.city_portal_last_fetch).total_seconds() > self.city_portal_cache_expiration:
            try:
                logger.debug('Getting city portal data')
                data = _fetch_data(city_portal_url.format(self.language, self.location))
                data = data.get("data")
                if data:
                    self.city_portal_last_fetch = datetime.now()
                    self.city_portal_data = data
                else:
                    self.city_portal_data = {}
            except Exception as e:
                logger.error('Error getting city portal data. ' + str(e))
                logger.exception(e)
                self.city_portal_data = {}
        return self.city_portal_data
