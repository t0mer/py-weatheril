# weatheril
[![Downloads](https://static.pepy.tech/personalized-badge/weatheril?period=total&units=international_system&left_color=blue&right_color=green&left_text=Downloads)](https://pepy.tech/project/weatheril)
[![PyPI version](https://img.shields.io/pypi/v/weatheril)](https://pypi.org/project/weatheril/)
[![PyPI format](https://img.shields.io/pypi/format/weatheril)](https://pypi.org/project/weatheril/)
[![License](https://img.shields.io/pypi/l/weatheril)](https://github.com/t0mer/py-weatheril/blob/main/LICENSE)



weatheril is an unofficial [IMS](https://ims.gov.il) (Israel Meteorological Service) Python API wrapper.

It reads the public JSON data that powers the [ims.gov.il](https://ims.gov.il) website and returns it as Python objects: the current weather for a location, the daily and hourly forecast, radar and satellite images, and active weather warnings. It is useful for scripts, bots and home-automation integrations that need Israeli weather data in Hebrew or English.

> **Disclaimer:** this project is not affiliated with, endorsed by, or supported by the Israel Meteorological Service. The data belongs to IMS and is subject to the terms of use published on [ims.gov.il](https://ims.gov.il). <!-- TODO: verify: link the exact IMS terms-of-use page --> The IMS endpoints are undocumented and can change without notice.

## Table of contents
* [Features supported](#features-supported)
* [Components and Frameworks used in weatheril](#components-and-frameworks-used-in-weatheril)
* [Requirements](#requirements)
* [Getting started](#getting-started)
* [Working with the API](#working-with-the-api)
* [Get Satellite and Radar Images](#get-satellite-and-radar-images)
* [Get current weather status for given location](#get-current-weather-status-for-given-location)
* [Get weather forecast](#get-weather-forecast)
* [Get weather warnings](#get-weather-warnings)
* [How it works](#how-it-works)
* [Caching](#caching)
* [Logging](#logging)
* [Known limitations](#known-limitations)
* [Security notes](#security-notes)
* [Development](#development)
* [Contributing](#contributing)
* [License](#license)

## Features supported
* Get current weather status (analysis) for a location.
* Get the daily and hourly forecast for every day IMS publishes (currently 7 days, including today).
* Get the country-level text forecast for each day.
* Get radar and satellite images, and turn them into animated GIFs.
* Get active weather warnings for the region of a location.
* Hebrew (`he`) and English (`en`) names and descriptions.
* Built-in caching of IMS responses.


## Components and Frameworks used in weatheril
* [Loguru](https://pypi.org/project/loguru/)
* [Requests](https://pypi.org/project/requests/)
* [Pillow](https://pypi.org/project/Pillow/)
* [pytz](https://pypi.org/project/pytz/)
* [urllib3](https://pypi.org/project/urllib3/)


## Requirements
* Python 3.10 or newer. The package metadata says `>=3.6`, but the code uses `int | None` style type hints that fail to import on Python 3.9 and older.
* Outbound HTTPS access to `ims.gov.il` over IPv4.
* No API key or account is needed.


## Getting started

Clone the repository and install it:

```bash
git clone https://github.com/t0mer/py-weatheril.git
cd py-weatheril
pip3 install .
```

### Installing from PyPI

```bash
# For Windows

pip install --upgrade weatheril

# For Linux | macOS

pip3 install --upgrade weatheril
```

## Working with the API

weatheril can be configured to retrieve forecast information for a specific location. When initiating the library you must set the location id, and you can set the language (currently only `he` and `en` are supported).

```python
from weatheril import WeatherIL
weather = WeatherIL(21, "he")
```

In the above example I set **Raanana** as the location and **Hebrew** as the language.

The constructor signature is:

```python
WeatherIL(location, language="he", cache_expiration_in_sec=30)
```

| Argument | Default | Description |
| --- | --- | --- |
| `location` | (required) | IMS location id (`int` or `str`), see the table below. |
| `language` | `"he"` | `"he"` (Hebrew) or `"en"` (English). Controls location names, weather descriptions and day names. |
| `cache_expiration_in_sec` | `30` | How long, in seconds, current analysis, forecast and warnings data is reused before it is fetched again. See [Caching](#caching). |

The public methods are:

| Method | Returns |
| --- | --- |
| `get_current_analysis()` | `Weather` object, or `None` on error |
| `get_forecast()` | `Forecast` object; `days` is empty if the request fails, and `None` is returned only on a parse error |
| `get_radar_images()` | `RadarSatellite` object (lists may be empty on error) |
| `get_warnings()` | list of `Warning` objects; raises `ValueError` if the location or its region is unknown. Other exceptions (e.g. `KeyError`, or the original error) can propagate if IMS lookup endpoints fail |

Full locations list in the table below. It was taken from the IMS [`locations_info`](https://ims.gov.il/en/locations_info) endpoint in September 2026. IMS adds and renames locations from time to time, so check that endpoint for the current list.

| Id | Location |
| ------------ | ----------- |
| 1| Jerusalem|
| 2| Tel Aviv Coast|
| 3| Haifa|
| 4| Rishon le Zion|
| 5| Petah Tiqva|
| 6| Ashdod|
| 7| Netania|
| 8| Beer Sheva|
| 9| Bnei Brak|
| 10| Holon|
| 11| Ramat Gan|
| 12| Asheqelon|
| 13| Rehovot|
| 14| Bat Yam|
| 15| Bet Shemesh|
| 16| Kfar Sava|
| 17| Herzliya|
| 18| Hadera|
| 19| Modiin|
| 20| Ramla|
| 21| Raanana|
| 22| Modiin Illit|
| 23| Rahat|
| 24| Hod Hasharon|
| 25| Givatayim|
| 26| Kiryat Ata|
| 27| Nahariya|
| 28| Beitar Illit|
| 29| Um al-Fahm|
| 30| Kiryat Gat|
| 31| Eilat|
| 32| Rosh Haayin|
| 33| Afula|
| 34| Nes-Ziona|
| 35| Akko|
| 36| Elad|
| 37| Ramat Hasharon|
| 38| Karmiel|
| 39| Yavneh|
| 40| Tiberias|
| 41| Tayibe|
| 42| Kiryat Motzkin|
| 43| Shfaram|
| 44| Nof Hagalil|
| 45| Kiryat Yam|
| 46| Kiryat Bialik|
| 47| Kiryat Ono|
| 48| Maale Adumim|
| 49| Or Yehuda|
| 50| Zefat|
| 51| Netivot|
| 52| Dimona|
| 53| Tamra|
| 54| Sakhnin|
| 55| Yehud-Monosson|
| 56| Baka al-Gharbiya|
| 57| Ofakim|
| 58| Givat Shmuel|
| 59| Tira|
| 60| Arad|
| 61| Migdal Haemek|
| 62| Sderot|
| 63| Araba|
| 64| Nesher|
| 65| Kiryat Shmona|
| 66| Yokneam Illit|
| 67| Kafr Qassem|
| 68| Kfar Yona|
| 69| Qalansawa|
| 70| Kiryat Malachi|
| 71| Maalot-Tarshiha|
| 72| Tirat Carmel|
| 73| Ariel|
| 74| Or Akiva|
| 75| Bet Shean|
| 76| Mizpe Ramon|
| 77| Lod|
| 78| Nazareth|
| 79| Qazrin|
| 80| En Gedi|
| 81| Ganei Tikva|
| 82| Beer Yaakov|
| 83| Maghar|
| 84| Tel Aviv - Yafo|
| 200| Nimrod Fortress|
| 201| Banias|
| 202| Tel Dan|
| 203| Snir Stream|
| 204| Horshat Tal|
| 205| Ayun Stream|
| 206| Hula|
| 207| Tel Hazor|
| 208| Akhziv|
| 209| Yehiam Fortress|
| 210| Baram|
| 211| Amud Stream|
| 212| Korazim|
| 213| Kfar Nahum|
| 214| Majrase|
| 215| Meshushim Stream|
| 216| Yehudiya|
| 217| Gamla|
| 218| Kursi|
| 219| Hamat Tiberias|
| 220| Arbel|
| 221| En Afek|
| 222| Tzipori|
| 223| Hai-Bar Carmel|
| 224| Mount Carmel|
| 225| Bet Shearim|
| 226| Mishmar HaCarmel|
| 227| Nahal Me‘arot|
| 228| Dor-HaBonim|
| 229| Tel Megiddo|
| 230| Kokhav HaYarden|
| 231| Maayan Harod|
| 232| Bet Alpha|
| 233| Gan HaShlosha|
| 235| Taninim Stream|
| 236| Caesarea|
| 237| Tel Dor|
| 238| Mikhmoret Sea Turtle|
| 239| Beit Yanai|
| 240| Apollonia|
| 241| Mekorot HaYarkon|
| 242| Palmahim|
| 243| Castel|
| 244| En Hemed|
| 245| City of David|
| 246| Me‘arat Soreq|
| 248| Bet Guvrin|
| 249| Sha’ar HaGai|
| 250| Migdal Tsedek|
| 251| Haniya Spring|
| 252| Sebastia|
| 253| Mount Gerizim|
| 254| Nebi Samuel|
| 255| En Prat|
| 256| En Mabo‘a|
| 257| Qasr al-Yahud|
| 258| Good Samaritan|
| 259| Euthymius Monastery|
| 261| Qumran|
| 262| Enot Tsukim|
| 263| Herodium|
| 264| Tel Hebron|
| 267| Masada|
| 268| Tel Arad|
| 269| Tel Beer Sheva|
| 270| Eshkol|
| 271| Mamshit|
| 272| Shivta|
| 273| Ben-Gurion’s Tomb|
| 274| En Avdat|
| 275| Avdat|
| 277| Hay-Bar Yotvata|
| 278| Coral Beach|
| 613| Tel Yosef|
| 702| Gilgal|
| 703| Maale Gilboa|
| 704| Makhtesh Ramon|
| 705| Neot Semadar|
| 706| Red Canyon|
| 707| Hazeva|
| 708| Bruchin|
| 709| Itamar|
| 710| Tal Menashe|
| 711| Rosh Zorim|
| 712| Nokdim|
| 713| Qiryat Arba|
| 714| Sosia|
| 715| Negohot|
| 717| Mount Hermon|
| 718| Mevaseret Zion|
| 719| Pardes Hanna-Karkur|


### Get Satellite and Radar Images

```python
from weatheril import WeatherIL
weather = WeatherIL(21, "he")
images = weather.get_radar_images()
```
The `get_radar_images` method will return a `RadarSatellite` object with four lists of full image URLs (`https://ims.gov.il/sites/default/files/ims_data/map_images/...`):
* `imsradar_images` - Rain radar images (IMS).
* `radar_images` - Radar composite images.
* `middle_east_satellite_images` - Middle East weather satellite images (the IMS "natural color" satellite product).
* `europe_satellite_images` - Europe weather satellite images. **Currently always empty**: the IMS `radar_satellite` data no longer contains a Europe entry.

You can also create an animated GIF from these image lists by using the `create_animation` method as follows:

```python
from weatheril import WeatherIL
weather = WeatherIL(21, "he")
images = weather.get_radar_images()
animated = images.create_animation(images=images.middle_east_satellite_images, animated_file="file.gif", path="/tmp")
```
The method downloads every image to the system temp directory, builds the GIF, deletes the downloaded frames and returns the path of the created GIF (or `None` on error). If `path` does not exist, the GIF is written into the installed `weatheril` package directory instead.

Note that `create_animation` replaces the URLs in the list you pass with local temp file paths. Every `RadarSatellite()` shares the same default lists, so fetching again does not help. Pass a copy instead, for example `images=list(images.middle_east_satellite_images)`.

**Optional**

You can use the following method to create animated GIFs for all image lists. It writes `imsradar.gif`, `radar.gif`, `middle_east.gif` and `europe.gif` (the last one is skipped with an error log while the Europe list is empty):

```python
from weatheril import WeatherIL
weather = WeatherIL(21, "he")
images = weather.get_radar_images()
images.generate_images(path="Path to store the images")
```


[![Satellite](https://github.com/t0mer/py-weatheril/blob/main/screenshots/animated.gif?raw=true "Satellite")](https://github.com/t0mer/py-weatheril/blob/main/screenshots/animated.gif?raw=true "Satellite")


### Get current weather status for given location

```python
from weatheril import WeatherIL
weather = WeatherIL(21, "he")
current = weather.get_current_analysis()
print(current.location, current.temperature, current.description)
```

The result will be a `Weather` object containing the data requested:

| Field | Type | Description |
| --- | --- | --- |
| `lid` | `str` | Location id. |
| `location` | `str` | Location name in the selected language. |
| `forecast_time` | `datetime` | Time of the analysis (Asia/Jerusalem timezone). |
| `modified_at` | `datetime` | When IMS last updated the record. |
| `temperature` | `float` | Temperature (°C). |
| `feels_like` | `float` or `None` | "Feels like" temperature (°C). |
| `humidity` | `int` | Relative humidity (%). |
| `due_point_temp` | `int` | Dew point temperature (°C). The field name follows the IMS spelling. |
| `rain` | `float` | Rain amount. |
| `rain_chance` | `int` | Chance of rain (%). |
| `wind_speed` | `int` | Wind speed. |
| `gust_speed` | `int` or `None` | Wind gust speed. |
| `wind_direction_id` | `int` | IMS wind direction id. |
| `wind_direction` | `int` | Wind direction as an azimuth in degrees (for example `248`), or `-1` if unknown. |
| `wind_chill` | `int` | Wind chill. |
| `heat_stress_level` | `int` | IMS heat stress level. |
| `u_v_index` | `int` | UV index. |
| `u_v_level` | `str` or `None` | UV level code (for example `L`, `M`). |
| `u_v_i_max` | `int` or `None` | Maximum UV index. |
| `u_v_i_factor` | `float` or `None` | UV factor. |
| `min_temp` / `max_temp` | `int` or `None` | Minimum / maximum temperature. |
| `pm10` | `int` | PM10 particle level. |
| `wave_height` | `float` | Wave height (coastal locations). |
| `weather_code` | `int` or `None` | IMS weather code. |
| `description` | `str` | Weather description in the selected language (`"Nothing"` if there is no code). |
| `language` | `str` | The language used. |
| `json` | `dict` | The raw IMS record, shown below. |

The raw `json` record looks like this (location 21, English):

```json
{
  "id": "14806397",
  "lid": "21",
  "forecast_time": "2026-09-29 14:40:00",
  "type": "forecast",
  "main_hour": "0",
  "heat_stress": "24.3",
  "relative_humidity": "49",
  "due_point_Temp": "16",
  "rain": "0.00",
  "temperature": "28.0",
  "wind_direction_id": "12",
  "wind_speed": 11,
  "wind_chill": "31",
  "weather_code": "1230",
  "heat_stress_level": "1",
  "feels_like": "29",
  "min_temp": "28",
  "max_temp": "28",
  "modified": "2026-09-29 09:55:00",
  "created": "2026-09-22 09:06:59",
  "u_v_index": "5",
  "u_v_level": "M",
  "u_v_i_max": "0",
  "u_v_i_factor": "0",
  "rain_chance": "0",
  "wave_height": null,
  "pm10": "21",
  "gust_speed": "23",
  "forecast_hour": "14"
}
```

### Get weather forecast


```python
from weatheril import WeatherIL
weather = WeatherIL(21, "he")
forecast = weather.get_forecast()
for day in forecast.days:
    print(day.date.date(), day.day, day.minimum_temperature, day.maximum_temperature, day.weather)
```

This method will return a `Forecast` object that includes the weather forecast for every day IMS publishes (currently 7 days, starting today). The object contains data on country level (the `description` text) and also on the given location: Forecast >> Daily >> Hourly. The hourly list for today starts at the current hour.

```python
class Forecast:
    days: list[Daily]

class Daily:
    language: str
    date: datetime             # midnight, Asia/Jerusalem
    lid: str
    location: str              # location name
    day: str                   # day of the week, in the selected language
    weather_code: int | None
    weather: str               # weather description
    minimum_temperature: int
    maximum_temperature: int
    maximum_uvi: int
    u_v_i_factor: float | None
    description: str           # country-level text forecast for the day
    hours: list[Hourly]

class Hourly:
    language: str
    hour: str                  # for example "14:00"
    forecast_time: datetime
    created: datetime
    weather_code: int | None
    weather: str               # weather description
    temperature: int | None
    precise_temperature: float | None
    heat_stress: float | None
    heat_stress_level: int | None
    pm10: int | None
    relative_humidity: int | None
    rain: float | None
    rain_chance: int | None
    wind_speed: int | None
    gust_speed: int | None
    wind_direction_id: int | None
    wind_direction: int        # azimuth in degrees, -1 if unknown
    wind_chill: int | None
    wave_height: float | None
    u_v_index: int | None
    u_v_i_max: int | None
```

### Get weather warnings

```python
from weatheril import WeatherIL
weather = WeatherIL(21, "en")
for warning in weather.get_warnings():
    print(warning.severity, warning.warning_type, warning.valid_from, warning.valid_to)
    print(warning.text_full)
```

`get_warnings()` returns the IMS warnings issued for the forecast region of the location (for example, all warnings for the region that contains Raanana). It returns an empty list when there are none, and raises `ValueError` if the location id or its region is unknown. Other exceptions (e.g. `KeyError`, or the original error) can propagate if IMS lookup endpoints fail.

Each `Warning` object has these fields:

| Field | Type | Description |
| --- | --- | --- |
| `location_id` | `int` | The location id you passed to `WeatherIL`. |
| `region_name` | `str` | Name of the location's warning region. |
| `wid`, `alert_id` | `int` | IMS warning and alert ids. |
| `severity_id` / `severity` | `int` / `str` | Severity id and its name. |
| `warning_type_id` / `warning_type` | `int` / `str` | Warning type id and its name. |
| `sent`, `valid_from`, `valid_to` | `datetime` | Timestamps (Asia/Jerusalem timezone). |
| `valid_from_unix` | `int` | Start time as a Unix timestamp. |
| `text` | `str` | Short warning text. |
| `text_full` | `str` | Full warning text. If IMS leaves it empty, it is filled from `full_en` or `full_he` according to the language. |
| `full_en`, `full_he` | `str` | Full text in English and Hebrew. |
| `groups` | `list[str]` | Names of the warning groups. |
| `regions` | `list[str]` | Names of all regions the warning applies to. |
| `language` | `str` | The language used. |

Tip: import the class you need by name (`from weatheril import WeatherIL`). `from weatheril import *` also imports the package's `Warning` class, which shadows Python's built-in `Warning`.


## How it works

weatheril calls the same JSON endpoints that the IMS website uses, under `https://ims.gov.il/{language}/`:

| Endpoint | Used for |
| --- | --- |
| `now_analysis/{location}` | Current weather (`get_current_analysis`) |
| `full_forecast_data/{location}` | Daily and hourly forecast (`get_forecast`) |
| `radar_satellite` | Radar and satellite image lists (`get_radar_images`) |
| `warnings` | Active warnings (`get_warnings`) |
| `locations_info` | Location names and regions |
| `weather_codes` | Weather descriptions |
| `wind_directions` | Wind direction id to azimuth |
| `regions` | Warning region names |
| `warnings_metadata` | Warning types, groups and severities |

Dates are parsed as timezone-aware `datetime` objects in the `Asia/Jerusalem` timezone. If the `weather_codes` endpoint cannot be reached, weather descriptions fall back to the list bundled in `weatheril/consts.py`.

**IPv6 is disabled on import.** ims.gov.il is reached over IPv4, and `requests` would otherwise try IPv6 first and wait for a timeout. Importing `weatheril` sets `requests.packages.urllib3.util.connection.HAS_IPV6 = False`, which affects every `requests`/`urllib3` call in the same Python process.


## Caching

There are two cache layers:

* **Per `WeatherIL` object:** current analysis, forecast and warnings data is kept for `cache_expiration_in_sec` seconds (default `30`).
* **Per process:** every IMS response is cached in memory by URL. Current analysis, forecast and warnings data use the same `cache_expiration_in_sec` TTL; `get_radar_images()` and the lookup endpoints use a 5-minute (300 s) TTL. This cache is on `main` (after 0.41.0).

Lookup tables (location names, weather descriptions, wind directions, regions, warning metadata) are loaded **once per process, in the language of the first request**, and are not refreshed. If you create a `WeatherIL(21, "he")` and then a `WeatherIL(21, "en")` in the same process, the second object still gets Hebrew names and descriptions. Use one language per process, or run separate processes for each language.


## Logging

weatheril logs with [Loguru](https://pypi.org/project/loguru/), including debug messages for every request. To silence it:

```python
from loguru import logger
logger.disable("weatheril")
```

`get_radar_images()` also prints progress lines (`Getting IMS Radar`, ...) to standard output.


## Known limitations

* `europe_satellite_images` is always empty, because IMS no longer publishes a Europe entry in its `radar_satellite` data.
* Only the "natural color" Middle East satellite product is returned. IMS also publishes `DUST`, `IR` and `FOG` products, which are not exposed.
* Every `RadarSatellite()` shares the same default lists, so the lists are shared between `get_radar_images()` calls and each call keeps adding URLs to them, giving duplicates. Copy the lists you need (for example `list(images.radar_images)`) and clear them before polling again.
* If the `locations_info` or `wind_directions` endpoint fails, location names show as `"Nothing"` and `wind_direction` as `-1`. The fallback lists bundled in `weatheril/consts.py` do not work for these lookups.
* HTTP requests are made without a timeout, so a stalled connection to ims.gov.il can block the call.
* See also the language note under [Caching](#caching).


## Security notes

* weatheril only sends unauthenticated HTTPS `GET` requests to `ims.gov.il` and stores no credentials.
* Importing the package disables IPv6 for `requests`/`urllib3` in the whole process (see [How it works](#how-it-works)). Keep that in mind when you embed it in a larger application.
* `create_animation()` downloads images to the system temp directory and deletes them afterwards. Pass an existing `path`, or the GIF is written into the package's install directory.


## Development

```bash
git clone https://github.com/t0mer/py-weatheril.git
cd py-weatheril
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install pytest
pytest tests/test_optimizations.py
```

Project layout:

| Path | Contents |
| --- | --- |
| `weatheril/__init__.py` | `WeatherIL` class and public API |
| `weatheril/weather.py` | `Weather` model (current analysis) |
| `weatheril/forecast.py` | `Forecast`, `Daily` and `Hourly` models |
| `weatheril/warning.py` | `Warning` model |
| `weatheril/radar_satellite.py` | `RadarSatellite` model and GIF creation |
| `weatheril/utils.py` | HTTP fetching, caching and lookup helpers |
| `weatheril/consts.py` | IMS URLs and bundled fallback lookup data |
| `tests/` | Unit tests and profiling scripts (mocked, no network) |

New versions are published to [PyPI](https://pypi.org/project/weatheril/) by the [`Publish pypi package`](https://github.com/t0mer/py-weatheril/blob/main/.github/workflows/python-publish.yml) GitHub Actions workflow, which runs when a GitHub release is published or when it is started manually.


## Contributing

Issues and pull requests are welcome at [github.com/t0mer/py-weatheril](https://github.com/t0mer/py-weatheril). Please keep changes focused, and include a short description of the IMS data you tested against.


## License

weatheril is released under the [MIT License](https://github.com/t0mer/py-weatheril/blob/main/LICENSE).
