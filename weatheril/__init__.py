"""Israel Meteorological Service unofficial python api wrapper"""
from datetime import datetime

import pytz
import requests
from loguru import logger
from weatheril.consts import CURRENT_ANALYSIS_URL, FORECAST_URL, IMS_API_URL_BASE, RADAR_SATELLITE_URL

from .forecast import Forecast, Daily, Hourly
from .radar_satellite import RadarSatellite
from .utils import get_value, fetch_data, get_data
from .weather import Weather

# ims.gov.il does not support ipv6 yet, `requests` use ipv6 by default
# and wait for timeout before trying ipv4, so we have to disable ipv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False

timezone = pytz.timezone("Asia/Jerusalem")

DAILY_KEY = "daily"
HOURLY_KEY = "hourly"


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
                forecast_time_str = get_value(
                    analysis_data, "forecast_time", None, str
                )
                forecast_time = (
                    timezone.localize(
                        datetime.strptime(forecast_time_str, "%Y-%m-%d %H:%M:%S")
                    )
                    if forecast_time_str
                    else None
                )

                modified_at_str = get_value(analysis_data, "modified", None, str)
                modified_at = (
                    timezone.localize(
                        datetime.strptime(modified_at_str, "%Y-%m-%d %H:%M:%S")
                    )
                    if modified_at_str
                    else None
                )

                return Weather(
                    langauge=self.language,
                    lid=get_value(analysis_data, "lid", None, str),
                    humidity=get_value(
                        analysis_data, "relative_humidity", None, int, 0
                    ),
                    rain=get_value(analysis_data, "rain", None, float, 0.0, -999.0),
                    rain_chance=get_value(analysis_data, "rain_chance", None, int, 0),
                    temperature=get_value(
                        analysis_data, "temperature", None, float, 0.0
                    ),
                    due_point_temp=get_value(
                        analysis_data, "due_point_Temp", None, int, 0
                    ),
                    wind_speed=get_value(analysis_data, "wind_speed", None, int, 0),
                    wind_chill=get_value(analysis_data, "wind_chill", None, int, 0),
                    wind_direction_id=get_value(
                        analysis_data, "wind_direction_id", None, int, 0
                    ),
                    feels_like=get_value(
                        analysis_data, "feels_like", None, float, 0.0
                    ),
                    heat_stress_level=get_value(
                        analysis_data, "heat_stress_level", None, int, 0
                    ),
                    u_v_index=get_value(analysis_data, "u_v_index", None, int, 0),
                    u_v_level=get_value(analysis_data, "u_v_level", None, str),
                    u_v_i_max=get_value(analysis_data, "u_v_i_max", None, int),
                    u_v_i_factor=get_value(analysis_data, "u_v_i_factor", None, float),
                    wave_height=get_value(
                        analysis_data, "wave_height", None, float, 0.0
                    ),
                    max_temp=get_value(analysis_data, "max_temp", None, int),
                    min_temp=get_value(analysis_data, "min_temp", None, int),
                    pm10=get_value(analysis_data, "pm10", None, int, 0),
                    forecast_time=forecast_time,
                    modified_at=modified_at,
                    json=analysis_data,
                    weather_code=get_value(analysis_data, "weather_code", None, int),
                    gust_speed=get_value(analysis_data, "gust_speed", None, int, None, -999)
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
                    get_value(forecast_data, key, HOURLY_KEY, dict)
                )
                daily = Daily(
                    language=self.language,
                    date=timezone.localize(datetime.strptime(key, "%Y-%m-%d")),
                    lid=get_value(
                        forecast_data[key], DAILY_KEY, "lid", default_value="0"
                    ),
                    weather_code=get_value(
                        forecast_data[key], DAILY_KEY, "weather_code", int
                    ),
                    minimum_temperature=get_value(
                        forecast_data[key], DAILY_KEY, "minimum_temperature", int
                    ),
                    maximum_temperature=get_value(
                        forecast_data[key], DAILY_KEY, "maximum_temperature", int
                    ),
                    maximum_uvi=get_value(
                        forecast_data[key], DAILY_KEY, "maximum_uvi", int
                    ),
                    u_v_i_factor=get_value(
                        forecast_data[key], "daily", "u_v_i_factor", float
                    ),
                    hours=hours,
                    description=(
                        get_value(
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
                        weather_code=get_value(data, key, "weather_code", int),
                        temperature=get_value(data, key, "temperature", int),
                        precise_temperature=get_value(
                            data, key, "precise_temperature", float
                        ),
                        heat_stress=get_value(data, key, "heat_stress", float),
                        heat_stress_level=get_value(
                            data, key, "heat_stress_level", int
                        ),
                        pm10=get_value(data, key, "pm10", int),
                        relative_humidity=get_value(
                            data, key, "relative_humidity", int
                        ),
                        rain=get_value(data, key, "rain", float, None, -999.0),
                        rain_chance=get_value(data, key, "rain_chance", int),
                        wind_speed=get_value(data, key, "wind_speed", int),
                        gust_speed=get_value(data, key, "gust_speed", int, None, -999),
                        wind_direction_id=get_value(
                            data, key, "wind_direction_id", int
                        ),
                        wave_height=get_value(data, key, "wave_height", float),
                        wind_chill=get_value(data, key, "wind_chill", int),
                        u_v_index=get_value(data, key, "u_v_index", int, None, -8991),
                        u_v_i_max=get_value(data, key, "u_v_i_max", int),
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
            url = RADAR_SATELLITE_URL.format(language=self.language)
            data = fetch_data(url)
            base_url = IMS_API_URL_BASE.format(language="").rstrip("/")
            for key in data.get("data").get("types").get("IMSRadar"):
                rs.imsradar_images.append(base_url + key.get("file_name"))

            for key in data.get("data").get("types").get("radar"):
                rs.radar_images.append(base_url + key.get("file_name"))

            for key in data.get("data").get("types").get("MIDDLE-EAST"):
                rs.middle_east_satellite_images.append(
                    base_url + key.get("file_name")
                )

            for key in data.get("data").get("types").get("EUROPE"):
                rs.europe_satellite_images.append(base_url + key.get("file_name"))

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
        url = CURRENT_ANALYSIS_URL.format(language=self.language, location=self.location)
        self._analysis_data = get_data(
            self._analysis_data, url, self._analysis_last_fetch, self._cache_expiration_in_sec
        )
        if self._analysis_data:
            self._analysis_last_fetch = datetime.now()

    def _get_forecast_data(self):
        """
        Get the city forecast data
        """
        url = FORECAST_URL.format(language=self.language, location=self.location)
        self._forecast_data = get_data(
            self._forecast_data, url, self._forecast_last_fetch, self._cache_expiration_in_sec
        )
        if self._forecast_data:
            self._forecast_last_fetch = datetime.now()
