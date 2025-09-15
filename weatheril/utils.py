import json
from datetime import datetime
from typing import Type, Optional

import requests
from loguru import logger
from weatheril.consts import EN_LOCATIONS, EN_WEATHER_CODES, EN_WIND_DIRECTIONS, HE_LOCATIONS, HE_WEATHER_CODES, HE_WIND_DIRECTIONS, LOCATIONS_INFO_URL, WARNINGS_METADTA_URL, WEATHER_CODES_URL, WIND_DIRECTIONS_URL
from weatheril.consts import REGIONS_URL
from weatheril.consts import SEA_REGIONS_URL

# ims.gov.il does not support ipv6 yet, `requests` use ipv6 by default
# and wait for timeout before trying ipv4, so we have to disable ipv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False

_weather_code_map = {}
_locations_map = {}
_wind_direction_map = {}
_regions_map = {}
_sea_regions_map = {}
_warning_type_map = {}
_warning_group_map = {}
_warning_severity_map = {}

def get_weather_description_by_code(language: str, code: int | None) -> str:
    """
    Get the weather description by the weather code
    """
    global _weather_code_map
    if not _weather_code_map:
        _weather_code_map = _get_weather_codes(language)
    if not code:
        return "Nothing"
    return _weather_code_map.get(code, "Nothing")

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

def get_location_info_by_id(language: str, lid: str | int):
    """
    Converts location id to City name
    """
    lid = str(lid)
    global _locations_map
    if not _locations_map:
        _locations_map = _get_locations_map(language)
    return _locations_map.get(int(lid))

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


def get_wind_direction(language: str, direction_code: int) -> int:
    """
    Converts the wind direction code to azimuth
    """
    global _wind_direction_map
    if not _wind_direction_map:
        _wind_direction_map = _get_wind_direction_map(language)
    direction = _wind_direction_map.get(direction_code)
    if not direction:
        return -1
    if isinstance(direction, int):
        return direction
    return int(direction.get("direction"))

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

def get_sea_region_by_id(language: str, region_id: int):
    """
    Get Region Information by Id
    """
    global _sea_regions_map
    if not _sea_regions_map:
        _sea_regions_map = _get_sea_regions(language)
    if not _sea_regions_map:
        return None
    sea_region = _sea_regions_map.get(region_id)
    return sea_region


def _get_sea_regions(language) -> dict:
    """
    Get the Sea Regions Map from IMS
    """
    try:
        url = SEA_REGIONS_URL.format(language=language)
        data = fetch_data(url)
        return {int(v['rid']): v for v in data["data"].values()}
    except Exception as e:
        logger.error("Error getting directions info.. " + str(e))
        logger.exception(e)
        raise e


def get_region_by_id(language: str, region_id: str) -> dict:
    """
    Get Region Information by Id
    """
    global _regions_map
    if not _regions_map:
        _regions_map = _get_regions(language)
    if not _regions_map:
        return {}
    region = _regions_map.get(region_id, {})
    return region


def _get_regions(language) -> dict | None:
    """
    Get the Regions Map from IMS
    """
    try:
        url = REGIONS_URL.format(language=language)
        data = fetch_data(url)
        return {v["rid"]: v for v in data["data"]}
    except Exception as e:
        logger.error("Error getting Regions info.. " + str(e))
        logger.exception(e)
        raise e


def _get_warning_metadata(language) -> dict | None:
    """
    Get the Warning Types Map from IMS
    """
    try:
        url = WARNINGS_METADTA_URL.format(language=language)
        data = fetch_data(url)
        return data["data"]
    except Exception as e:
        logger.error("Error getting Warning Metadata... " + str(e))
        logger.exception(e)
        raise e

def get_warning_type_by_id(language: str, warning_type_id: int) -> dict:
    """
    Get the Warning Types by Id
    """
    global _warning_type_map
    global _warning_group_map
    global _warning_severity_map
    if not _warning_type_map:
        _warning_metadata = _get_warning_metadata(language)
        if _warning_metadata is None:
            raise ValueError("Warning Type Map not found")

        _warning_type_map = {int(v["warning_type_id"]): v for v in _warning_metadata["ims_warning_type"].values()}
        _warning_group_map = {k: v for k,v in _warning_metadata["warning_groups"].items()}
        _warning_severity_map = {int(v["severity_id"]): v for v in _warning_metadata["warning_severity"].values()}
    if not _warning_type_map:
        raise ValueError("Warning Type Map not found")
    return _warning_type_map.get(warning_type_id, {})

def get_warning_group_by_id(language: str, warning_group_id: str) -> dict:
    """
    Get the Warning Group by Id
    """
    global _warning_type_map
    global _warning_group_map
    global _warning_severity_map
    if not _warning_type_map:
        _warning_metadata = _get_warning_metadata(language)
        if _warning_metadata is None:
            return {}

        _warning_type_map = {int(v["warning_type_id"]): v for v in _warning_metadata["ims_warning_type"].values()}
        _warning_group_map = {k: v for k,v in _warning_metadata["warning_groups"].items()}
        _warning_severity_map = {int(v["severity_id"]): v for v in _warning_metadata["warning_severity"].values()}
    if not _warning_type_map:
        raise ValueError("Warning Group Map not found")
    return _warning_group_map.get(warning_group_id, {})

def get_warning_severity_by_id(language: str, warning_severity_id: int) -> dict:
    """
    Get the Warning Severity by Id
    """
    global _warning_type_map
    global _warning_group_map
    global _warning_severity_map
    if not _warning_type_map:
        _warning_metadata = _get_warning_metadata(language)
        if _warning_metadata is None:
            return {}

        _warning_type_map = {int(v["warning_type_id"]): v for v in _warning_metadata["ims_warning_type"].values()}
        _warning_group_map = {k: v for k,v in _warning_metadata["warning_groups"].items()}
        _warning_severity_map = {int(v["severity_id"]): v for v in _warning_metadata["warning_severity"].values()}
    if not _warning_severity_map:
        raise ValueError("Warning Severity Map not found")
    return _warning_severity_map.get(warning_severity_id, {})

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
