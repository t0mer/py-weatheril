# weatheril
[![Downloads](https://static.pepy.tech/personalized-badge/weatheril?period=total&units=international_system&left_color=blue&right_color=green&left_text=Downloads)](https://pepy.tech/project/weatheril) 
[![DownloaFormatds](https://img.shields.io/pypi/v/weatheril)](https://img.shields.io/pypi/v/weatheril)
[![DownloaFormatds](https://img.shields.io/pypi/format/weatheril)](https://img.shields.io/pypi/format/weatheril) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=techblog_weatheril&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=techblog_weatheril)



weatheril is an unofficial [IMS](https://ims.gov.il) (Israel Meteorological Service) python API wrapper.

## Features supported
* Get current weather status.
* Get Daily and Hourly forecast (5 days ahead).
* Get Radar and Satellite images.


## Components and Frameworks used in weatheril
* [Loguru](https://pypi.org/project/loguru/)
* [Requests ](https://pypi.org/project/requests/)
* [Pillow](https://pypi.org/project/Pillow/)
* [urllib3](https://pypi.org/project/urllib3/)


## Getting started

Use git to clone or you can also manually download the project repository just as shown below;

```bash
$ git clone https://github.com/t0mer/py-weatheril/
$ cd py-weatheril
py-weatheril $ python3 setup.py install 
```

### Installing from PyPi

```bash
# For Windows 

pip install  --upgrade weatheril

#For Linux | MAC 

pip3 install --upgrade weatheril
```

## Working with the API

weatheril can be configured to retrive forecast information for specific location. when initiating the library you must set the location id and language (Currently only he and en are supported)

```python
from weatheril import *
weather = WeatherIL(21,"he")
```

In the above example i set **Raanana** as the location and **Hebrew** as language. Full locations list in the table below.



| Id | Location |
| ------------ | ----------- |
| 1| Jerusalem|
| 2| Tel Aviv - Yafo|
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
| 53| Tamra |
| 54| Sakhnin|
| 55| Yehud|
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
| 200| Nimrod Fortress|
| 201| Banias|
| 202| Tel Dan|
| 203| Snir Stream|
| 204| Horshat Tal |
| 205| Ayun Stream|
| 206| Hula|
| 207| Tel Hazor|
| 208| Akhziv|
| 209| Yehiam Fortress|
| 210| Baram|
| 211| Amud Stream|
| 212| Korazim|
| 213| Kfar Nahum|
| 214| Majrase |
| 215| Meshushim Stream|
| 216| Yehudiya |
| 217| Gamla|
| 218| Kursi |
| 219| Hamat Tiberias|
| 220| Arbel|
| 221| En Afek|
| 222| Tzipori|
| 223| Hai-Bar Carmel|
| 224| Mount Carmel|
| 225| Bet Shearim|
| 226| Mishmar HaCarmel |
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
| 267| Masada |
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


### Get Satellite and Radar Images

```python
from weatheril import *
weather = WeatherIL(21,"he")
images = weather.get_radar_images()
```
The get_radar_images will retun an object with four lists:
* imsradar_images - Rain radar images (IMS).
* radar_images - Radar images.
* middle_east_satellite_images - Middel East weather sattelite images.
* europe_satellite_images - Eourope weather sattelite images.

You can also create animateg gif from this images lists by using the create_animation method as follows:

```python
from weatheril import *
weather = WeatherIL(21,"he")
images = weather.get_radar_images()
animated = images.create_animation(images = images.middle_east_satellite_images, animated_file = "file.gif", path="/tmp")
```
The function will return the path for the created image.

**Optional**
You can use the following function to create animated gifs for all images

```python
from weatheril import *
weather = WeatherIL(21,"he")
images = weather.get_radar_images()
images.generate_images(path="Path to store the images")
```


[![Sattelite](https://github.com/t0mer/py-weatheril/blob/main/screenshots/animated.gif?raw=true "Sattelite")](https://github.com/t0mer/py-weatheril/blob/main/screenshots/animated.gif?raw=true "Sattelite")


### Get current weather status for given location

```python
from weatheril import *
weather = WeatherIL(21,"he")
current = weather.get_current_analysis()
```

The result will be a weather object containing the data requested:
* Location.
* Humidity.
* Rain.
* Temperature.
* Wind speed.
* Feels like.
* UV.
* Time
* Json result

```json
       "33": {
            "id": "1601809",
            "lid": "33",
            "forecast_time": "2023-01-25 16:00:00",
            "type": "analysis",
            "main_hour": "0",
            "heat_stress": "17",
            "relative_humidity": "58",
            "due_point_Temp": "11",
            "rain": null,
            "temperature": "20",
            "wind_direction_id": "15",
            "wind_speed": "2",
            "wind_chill": "20",
            "weather_code": null,
            "heat_stress_level": "0",
            "feels_like": "20",
            "min_temp": null,
            "max_temp": null,
            "modified": "2023-01-25 15:55:00",
            "created": "2023-01-22 11:50:05",
            "u_v_index": "0",
            "u_v_level": "L",
            "u_v_i_max": null,
            "u_v_i_factor": null
        }
```

### Get weather forecast


```python
from weatheril import *
weather = WeatherIL(21,"he")
forcats = weather.get_forecast()
```

This method wil return forecast object that includes weather forecast for the new 5 days. The object contains data on Coutry level and also on give location Forecast >> Daily >> Hourly.

```python

class Forecast:
    days: list

class Daily:
    date: datetime
    location: str
    day: str
    weather: str
    minimum_temperature: int
    maximum_temperature: int
    maximum_uvi: int
    hours: list
    description: str

class Hourly:
    hour: str
    weather: str
    temperature: int


```
