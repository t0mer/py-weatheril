import json
from datetime import datetime
from typing import Type, Optional

import requests
from loguru import logger
from weatheril.consts import EN_LOCATIONS, EN_WEATHER_CODES, EN_WIND_DIRECTIONS, HE_LOCATIONS, HE_WEATHER_CODES, HE_WIND_DIRECTIONS, LOCATIONS_INFO_URL, WEATHER_CODES_URL, WIND_DIRECTIONS_URL

# ims.gov.il does not support ipv6 yet, `requests` use ipv6 by default
# and wait for timeout before trying ipv4, so we have to disable ipv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False

_weather_code_map = {}
_locations_map = {}
_wind_direction_map = {}

def get_weather_description_by_code(language: str, code: int) -> str:
    """
    Get the weather description by the weather code
    """
    global _weather_code_map
    if not _weather_code_map:
        _weather_code_map = _get_weather_codes(language)
    return _weather_code_map.get(code)

def _get_weather_codes(language) -> dict:
    """
    Get the weather codes from IMS
    """
    try:
        url = WEATHER_CODES_URL.format(language=language)
        data = fetch_data(url)
        return {int(d["id"]): d["desc"] for d in data["data"].values()}
    except Exception as e:
        logger.error("Error getting weather codes. " + str(e))
        logger.exception(e)
        return HE_WEATHER_CODES if language == "he" else EN_WEATHER_CODES


def get_location_name_by_id(language: str, lid: str | int):
    """
    Converts location id to City name
    """
    lid = str(lid)
    global _locations_map
    if not _locations_map:
        _locations_map = _get_locations_map(language)
    location = _locations_map.get(lid)
    return location["name"] if location else "Nothing"

def _get_locations_map(language) -> dict:
    """
    Get the location information from IMS
    """
    try:
        url = LOCATIONS_INFO_URL.format(language=language)
        data = fetch_data(url)
        return {int(d["lid"]): d for d in data["data"].values()}
    except Exception as e:
        logger.error("Error getting locations info.. " + str(e))
        logger.exception(e)
        return HE_LOCATIONS if language == "he" else EN_LOCATIONS


def get_wind_direction(language: str, direction_code: int):
    """
    Converts the wind direction code to name
    """
    global _wind_direction_map
    if not _wind_direction_map:
        _wind_direction_map = _get_wind_direction_map(language)
    direction = _wind_direction_map.get(direction_code)
    if not direction:
        return "Nothing"
    if isinstance(direction, str):
        return direction
    return direction.get("text")

def _get_wind_direction_map(language) -> dict:
    """
    Get the Wind Direction Map from IMS
    """
    try:
        url = WIND_DIRECTIONS_URL.format(language=language)
        data = fetch_data(url)
        return {int(k): v for k, v in data["data"].items()}
    except Exception as e:
        logger.error("Error getting directions info.. " + str(e))
        logger.exception(e)
        return HE_WIND_DIRECTIONS if language == "he" else EN_WIND_DIRECTIONS


def get_day_of_the_week(language: str, date: datetime):
    """
    Converts the given date to day of the week name
    """
    weekday = {
        "Sunday": "ראשון",
        "Monday": "שני",
        "Tuesday": "שלישי",
        "Wednesday": "רביעי",
        "Thursday": "חמישי",
        "Friday": "שישי",
        "Saturday": "שבת",
    }
    day = date.strftime("%A")
    if language == "he":
        return weekday.get(day, "nothing")
    else:
        return day

def get_value(
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


def fetch_data(url: str) -> dict:
    """
    Helper method to get the Json data from ims website
    """
    try:
        logger.debug("Getting data from: " + url)
        response = requests.get(url)
        response = json.loads(response.text)
        return response
    except Exception as e:
        logger.error("Error getting data. " + str(e))
        logger.exception(e)
        return dict()


def get_data(current_data, url, last_fetch_time, cache_expiration_in_sec) -> dict:
    if (
        current_data
        and (datetime.now() - last_fetch_time).total_seconds()
        < cache_expiration_in_sec
    ):
        return current_data
    try:
        logger.debug("Getting data from " + url)
        return fetch_data(url).get("data", {})
    except Exception as e:
        logger.error("Error getting city portal data. " + str(e))
        logger.exception(e)
    return {}
