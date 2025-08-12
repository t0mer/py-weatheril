"""Israel Meteorological Service unofficial python api wrapper"""

import json
from typing import Type

import requests
import pytz
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

timezone = pytz.timezone("Asia/Jerusalem")

DAILY_KEY = "daily"
HOURLY_KEY = "hourly"


def _get_value(
    data: dict,
    key: str,
    inner_dict_key: Optional[str],
    data_type: Type = dict,
    default_value=None,
    custom_empty_value=None
):
    """
    Get default value from nested dictionary and convert to specified data type
    :param data: dictionary
    :param key: first level key
    :param inner_dict_key: second level key
    :param data_type: data type to convert to (str, int, float)
    :param default_value: default value
    :return: data[key][dict_key] or data[key] or default_value
    """
    value = None
    if key in data:
        if inner_dict_key is None:
            value = data.get(key)
        elif isinstance(data.get(key), dict) and inner_dict_key in data.get(key):
            value = data.get(key).get(inner_dict_key)

    if value is None:
        return default_value

    try:
        if data_type is str:
            value = str(value)
        if data_type is int:
            value = int(value)
        if data_type is float:
            value = float(value)
    except (ValueError, TypeError):
        value = default_value

    if custom_empty_value and value == custom_empty_value:
        return default_value
    return value


def _fetch_data(url: str) -> dict:
    """
    Helper method to get the Json data from ims website
    """
    try:
        response = requests.get(url)
        response = json.loads(response.text)
        return response
    except Exception as e:
        logger.error("Error getting data. " + str(e))
        logger.exception(e)
        return dict()


DEFAULT_CACHE_EXPIRATION = 30


class WeatherIL:
    def __init__(
        self, location, language="he", cache_expiration_in_sec=DEFAULT_CACHE_EXPIRATION
    ):
        """
        Init the WeatherIL object.
        parameters:
            >>> location: Location Id for the forecast (Table exists in the readme)
            >>> language: can be he (Hebrew) or en (English). default will be "he"
            >>> city_portal_cache_expiration: cache expiration in days for city portal data API. default is 30 seconds
        """
        self._cache_expiration_in_sec = cache_expiration_in_sec
        self.language = language
        self.location = str(location)
        self._analysis_data = None
        self._analysis_last_fetch = None
        self._forecast_data = None
        self._forecast_last_fetch = None

    def get_current_analysis(self):
        self._get_analysis_data()
        try:
            logger.debug("Getting current analysis")
            analysis_data = self._analysis_data.get(self.location, {})
            if analysis_data:
                logger.debug("Got current analysis for location " + str(self.location))
                # Parse forecast_time and modified_at separately due to datetime parsing
                forecast_time_str = _get_value(
                    analysis_data, "forecast_time", None, str
                )
                forecast_time = (
                    timezone.localize(
                        datetime.strptime(forecast_time_str, "%Y-%m-%d %H:%M:%S")
                    )
                    if forecast_time_str
                    else None
                )

                modified_at_str = _get_value(analysis_data, "modified", None, str)
                modified_at = (
                    timezone.localize(
                        datetime.strptime(modified_at_str, "%Y-%m-%d %H:%M:%S")
                    )
                    if modified_at_str
                    else None
                )

                return Weather(
                    langauge=self.language,
                    lid=_get_value(analysis_data, "lid", None, str),
                    humidity=_get_value(
                        analysis_data, "relative_humidity", None, int, 0
                    ),
                    rain=_get_value(analysis_data, "rain", None, float, 0.0, -999.0),
                    rain_chance=_get_value(analysis_data, "rain_chance", None, int, 0),
                    temperature=_get_value(
                        analysis_data, "temperature", None, float, 0.0
                    ),
                    due_point_temp=_get_value(
                        analysis_data, "due_point_Temp", None, int, 0
                    ),
                    wind_speed=_get_value(analysis_data, "wind_speed", None, int, 0),
                    wind_chill=_get_value(analysis_data, "wind_chill", None, int, 0),
                    wind_direction_id=_get_value(
                        analysis_data, "wind_direction_id", None, int, 0
                    ),
                    feels_like=_get_value(
                        analysis_data, "feels_like", None, float, 0.0
                    ),
                    heat_stress_level=_get_value(
                        analysis_data, "heat_stress_level", None, int, 0
                    ),
                    u_v_index=_get_value(analysis_data, "u_v_index", None, int, 0),
                    u_v_level=_get_value(analysis_data, "u_v_level", None, str),
                    u_v_i_max=_get_value(analysis_data, "u_v_i_max", None, int),
                    u_v_i_factor=_get_value(analysis_data, "u_v_i_factor", None, float),
                    wave_height=_get_value(
                        analysis_data, "wave_height", None, float, 0.0
                    ),
                    max_temp=_get_value(analysis_data, "max_temp", None, int),
                    min_temp=_get_value(analysis_data, "min_temp", None, int),
                    pm10=_get_value(analysis_data, "pm10", None, int, 0),
                    forecast_time=forecast_time,
                    modified_at=modified_at,
                    json=analysis_data,
                    weather_code=_get_value(analysis_data, "weather_code", None, int),
                    gust_speed=_get_value(analysis_data, "gust_speed", None, int, None, -999)
                )
            else:
                logger.error('No "' + self.location + '" in current analysis response')
                logger.debug("Response: " + analysis_data)
                return None
        except Exception as e:
            logger.error("Error getting current analysis.")
            logger.exception(e)
            return None

    def get_forecast(self):
        """
        Get weather forecast
        return: Forecast object
        """
        logger.debug("Getting forecast")
        self._get_forecast_data()
        try:
            days = []
            forecast_data = self._forecast_data
            logger.debug("Got forecast for location " + str(self.location))
            for key in forecast_data.keys():
                hours = self._get_hourly_forecast(
                    _get_value(forecast_data, key, HOURLY_KEY, dict)
                )
                daily = Daily(
                    language=self.language,
                    date=timezone.localize(datetime.strptime(key, "%Y-%m-%d")),
                    lid=_get_value(
                        forecast_data[key], DAILY_KEY, "lid", default_value="0"
                    ),
                    weather_code=_get_value(
                        forecast_data[key], DAILY_KEY, "weather_code", int
                    ),
                    minimum_temperature=_get_value(
                        forecast_data[key], DAILY_KEY, "minimum_temperature", int
                    ),
                    maximum_temperature=_get_value(
                        forecast_data[key], DAILY_KEY, "maximum_temperature", int
                    ),
                    maximum_uvi=_get_value(
                        forecast_data[key], DAILY_KEY, "maximum_uvi", int
                    ),
                    u_v_i_factor=_get_value(
                        forecast_data[key], "daily", "u_v_i_factor", float
                    ),
                    hours=hours,
                    description=(
                        _get_value(
                            forecast_data[key],
                            "country",
                            "description",
                            default_value="",
                        )
                    ).rstrip(),
                )
                days.append(daily)
            return Forecast(days)

        except Exception as e:
            logger.error("Error getting forecast data")
            logger.exception(e)
            return None

    def _get_hourly_forecast(self, data):
        """
        Get the hourly forecast
        """
        hours = []
        try:
            for key in data.keys():
                hours.append(
                    Hourly(
                        language=self.language,
                        hour=key,
                        forecast_time=timezone.localize(
                            datetime.strptime(
                                data.get(key, {}).get("forecast_time"),
                                "%Y-%m-%d %H:%M:%S",
                            )
                        ),
                        created=timezone.localize(
                            datetime.strptime(
                                data.get(key, {}).get("created"), "%Y-%m-%d %H:%M:%S"
                            )
                        ),
                        weather_code=_get_value(data, key, "weather_code", int),
                        temperature=_get_value(data, key, "temperature", int),
                        precise_temperature=_get_value(
                            data, key, "precise_temperature", float
                        ),
                        heat_stress=_get_value(data, key, "heat_stress", float),
                        heat_stress_level=_get_value(
                            data, key, "heat_stress_level", int
                        ),
                        pm10=_get_value(data, key, "pm10", int),
                        relative_humidity=_get_value(
                            data, key, "relative_humidity", int
                        ),
                        rain=_get_value(data, key, "rain", float, None, -999.0),
                        rain_chance=_get_value(data, key, "rain_chance", int),
                        wind_speed=_get_value(data, key, "wind_speed", int),
                        gust_speed=_get_value(data, key, "gust_speed", int, None, -999),
                        wind_direction_id=_get_value(
                            data, key, "wind_direction_id", int
                        ),
                        wave_height=_get_value(data, key, "wave_height", float),
                        wind_chill=_get_value(data, key, "wind_chill", int),
                        u_v_index=_get_value(data, key, "u_v_index", int, None, -8991),
                        u_v_i_max=_get_value(data, key, "u_v_i_max", int),
                    )
                )
            return hours
        except Exception as e:
            logger.error("Error getting hourly forecast ")
            logger.exception(e)
            return None

    def get_radar_images(self):
        """
        Get the list of images for Satellite and Radar
        return: RadarSatellite objects with the lists
        """
        rs = RadarSatellite()
        try:
            logger.debug("Getting radar images")
            data = _fetch_data(radar_url.format(self.language))
            for key in data.get("data").get("types").get("IMSRadar"):
                rs.imsradar_images.append(images_url + key.get("file_name"))

            for key in data.get("data").get("types").get("radar"):
                rs.radar_images.append(images_url + key.get("file_name"))

            for key in data.get("data").get("types").get("MIDDLE-EAST"):
                rs.middle_east_satellite_images.append(
                    images_url + key.get("file_name")
                )

            for key in data.get("data").get("types").get("EUROPE"):
                rs.europe_satellite_images.append(images_url + key.get("file_name"))

            logger.debug(f"\
                Got: {len(rs.imsradar_images)} IMS Radar Images;\
                {len(rs.radar_images)} Radar Images;\
                {len(rs.middle_east_satellite_images)} Middle East Satellite Images;\
                {len(rs.europe_satellite_images)} European Satellite Images")
            return rs
        except Exception as e:
            logger.error("Error getting images. " + str(e))
            return rs

    def _get_analysis_data(self):
        """
        Get the city current analysis data
        return: dict
        """
        self._analysis_data = self._get_data(
            self._analysis_data, current_analysis_url, self._analysis_last_fetch
        )
        if self._analysis_data:
            self._analysis_last_fetch = datetime.now()

    def _get_forecast_data(self):
        """
        Get the city forecast data
        """
        self._forecast_data = self._get_data(
            self._forecast_data, forecast_url, self._forecast_last_fetch
        )
        if self._forecast_data:
            self._forecast_last_fetch = datetime.now()

    def _get_data(self, current_data, url, last_fetch_time) -> dict:
        formatted_url = url.format(self.language, self.location)
        if (
            current_data
            and (datetime.now() - last_fetch_time).total_seconds()
            < self._cache_expiration_in_sec
        ):
            return current_data
        try:
            logger.debug("Getting data from " + formatted_url)
            return _fetch_data(formatted_url).get("data", {})
        except Exception as e:
            logger.error("Error getting city portal data. " + str(e))
            logger.exception(e)
        return {}
