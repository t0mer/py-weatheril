"""Israel Meteorological Service unofficial python api wrapper"""
import os
import json
import requests
import pandas as pd
from PIL import Image
from .forecast import Forecast, Daily, Hourly
from .weather import *
from loguru import logger
from urllib.parse import urlparse
from .radar_satellite import RadarSatellite
from datetime import datetime

images_url = "https://ims.gov.il"
locations_url = "https://ims.gov.il/{}/locations_info"
forecast_url = "https://ims.gov.il/{}/full_forecast_data/{}"
radar_url = "https://ims.gov.il/{}/radar_satellite"
current_analysis_url = "https://ims.gov.il/{}/now_analysis"
weather_codes_url = "https://ims.gov.il/{}/weather_codes"

# ims.gov.il does not support ipv6 yet, `requests` use ipv6 by default
# and wait for timeout before trying ipv4, so we have to disable ipv6
requests.packages.urllib3.util.connection.HAS_IPV6=False




class WeatherIL:
    def __init__(self, location,language="he"):
        """
        Init the WeatherIL object.
        parameters:
            >>> location: Location Id for the forecast (Table exists in the readme)
            >>> language: can be he (Hebrew) or en (English). default will be he
        """
        self.language = language
        self.location = str(location)

    def get_current_analysis(self):
        try:
            logger.debug('Getting current analysis')
            data = self.get_data(current_analysis_url.format(self.language))
            weather_data = data["data"][self.location]
            logger.debug('Got current analysis for location ' + str(self.location))
            weather = Weather(lid=weather_data["lid"],
                                location=self.get_location_name_by_id(weather_data["lid"]),
                                humidity=weather_data["relative_humidity"],
                                rain=weather_data["rain"],
                                temperature=weather_data["temperature"],
                                wind_speed=weather_data["wind_speed"],
                                feels_like=weather_data["feels_like"],
                                u_v_index=weather_data["u_v_index"],
                                forecast_time=weather_data["forecast_time"],
                                json = weather_data,
                                weather_code = weather_data["weather_code"],
                                description = self.get_weather_description_by_code(weather_data["weather_code"]))
            return weather
        except Exception as e:
            logger.error('Error getting current analysis. ' + str(e))
            return None
 
    def get_forecast(self):
        '''
        Get weather forecast
        return: Forecast object
        '''
        try:
            data = self.get_data(forecast_url.format(self.language,self.location))
            days = []
            for key in data["data"].keys():
                    day = self.get_day_of_the_week(key)
                    hours = self.get_hourly_forecast(data["data"][key]["hourly"])
                    if "description" in str(data):
                        try:
                            description = data["data"][key]["country"]["description"]
                        except:
                            description = ""
                    else:
                        description = ""
                    daily = Daily(
                        date = datetime.strptime(key, "%Y-%m-%d"),
                        location = self.get_location_name_by_id(data["data"][key]["daily"]["lid"]),
                        day = day,
                        weather=self.get_weather_description_by_code(data["data"][key]["daily"]["weather_code"]),
                        weather_code = data["data"][key]["daily"]["weather_code"],
                        minimum_temperature=data["data"][key]["daily"]["minimum_temperature"],
                        maximum_temperature=data["data"][key]["daily"]["maximum_temperature"],
                        maximum_uvi=data["data"][key]["daily"]["maximum_uvi"],
                        hours=hours,
                        description=description

                        )
                    days.append(daily)
            return Forecast(days)

        except Exception as e:
            logger.error("Error getting forecast data " + str(e))
            return None

    def get_hourly_forecast(self,data):
        '''
        Get the hourly forecast
        '''
        hours = []
        try:
            for key in data.keys():
                hours.append(
                    Hourly(key,datetime.strptime(data[key]["forecast_time"],"%Y-%m-%d %H:%M:%S"),
                    self.get_weather_description_by_code(data[key]["weather_code"]),
                    data[key]["weather_code"],int(data[key]["temperature"]),
                    heat_stress=int(data[key]["heat_stress"]),
                    relative_humidity=int(data[key]["relative_humidity"]),
                    rain=float(data[key]["relative_humidity"]),
                    wind_speed=int(data[key]["wind_speed"]),
                    wind_direction=self.get_wind_direction(data[key]["wind_direction_id"])))
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
            for key in data["data"]["types"]["IMSRadar"]:
                rs.imsradar_images.append(images_url + key["file_name"])

            for key in data["data"]["types"]["radar"]:
                rs.radar_images.append(images_url + key["file_name"])

            for key in data["data"]["types"]["MIDDLE-EAST"]:
                rs.middle_east_satellite_images.append(images_url + key["file_name"])

            for key in data["data"]["types"]["EUROPE"]:
                rs.europe_satellite_images.append(images_url + key["file_name"])

            logger.debug(f"\
                Got: {len(rs.imsradar_images)} IMS Radar Images;\
                {len(rs.radar_images)} Radar Images;\
                {len(rs.middle_east_satellite_images)} Middle East Satellite Images;\
                {len(rs.europe_satellite_images)} European Satellite Images")
            return rs
        except Exception as e:
            logger.error('Error getting images. ' + str(e))
            return rs

    def get_data(self,url):
        '''
        Helper method to get the Json data from ims website
        '''
        try:
            response = requests.get(url)
            response =  json.loads(response.text)
            return response
        except Exception as e:
            logger.error('Error getting data. ' + str(e))
            return ""

    def get_location_name_by_id(self,lid):
        '''
        Converts location id to City name
        '''
        
        HE_LOCATIONS = {
       "1": {
            "lid": "1",
            "name": "ירושלים",
            "lat": "31.7780",
            "lon": "35.2000",
            "zoom": "1",
            "height": "780",
            "is_park": "0"
        },
        "2": {
            "lid": "2",
            "name": "תל אביב-יפו",
            "lat": "32.0821",
            "lon": "34.7802",
            "zoom": "1",
            "height": "30",
            "is_park": "0"
        },
        "3": {
            "lid": "3",
            "name": "חיפה",
            "lat": "32.7900",
            "lon": "34.9900",
            "zoom": "1",
            "height": "250",
            "is_park": "0"
        },
        "4": {
            "lid": "4",
            "name": "ראשון לציון",
            "lat": "31.9640",
            "lon": "34.8040",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "5": {
            "lid": "5",
            "name": "פתח תקווה",
            "lat": "32.0869",
            "lon": "34.8882",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "6": {
            "lid": "6",
            "name": "אשדוד",
            "lat": "31.8011",
            "lon": "34.6410",
            "zoom": "1",
            "height": "30",
            "is_park": "0"
        },
        "7": {
            "lid": "7",
            "name": "נתניה",
            "lat": "32.3285",
            "lon": "34.8565",
            "zoom": "1",
            "height": "35",
            "is_park": "0"
        },
        "8": {
            "lid": "8",
            "name": "באר שבע",
            "lat": "31.2497",
            "lon": "34.7997",
            "zoom": "1",
            "height": "280",
            "is_park": "0"
        },
        "9": {
            "lid": "9",
            "name": "בני ברק",
            "lat": "32.0868",
            "lon": "34.8363",
            "zoom": "5",
            "height": "35",
            "is_park": "0"
        },
        "10": {
            "lid": "10",
            "name": "חולון",
            "lat": "32.0171",
            "lon": "34.7688",
            "zoom": "4",
            "height": "35",
            "is_park": "0"
        },
        "11": {
            "lid": "11",
            "name": "רמת גן",
            "lat": "32.0822",
            "lon": "34.8141",
            "zoom": "4",
            "height": "50",
            "is_park": "0"
        },
        "12": {
            "lid": "12",
            "name": "אשקלון",
            "lat": "31.6654",
            "lon": "34.5638",
            "zoom": "1",
            "height": "40",
            "is_park": "0"
        },
        "13": {
            "lid": "13",
            "name": "רחובות",
            "lat": "31.8982",
            "lon": "34.8085",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "14": {
            "lid": "14",
            "name": "בת ים",
            "lat": "32.0161",
            "lon": "34.7413",
            "zoom": "3",
            "height": "20",
            "is_park": "0"
        },
        "15": {
            "lid": "15",
            "name": "בית שמש",
            "lat": "31.7498",
            "lon": "34.9864",
            "zoom": "3",
            "height": "300",
            "is_park": "0"
        },
        "16": {
            "lid": "16",
            "name": "כפר סבא",
            "lat": "32.1726",
            "lon": "34.9080",
            "zoom": "3",
            "height": "55",
            "is_park": "0"
        },
        "17": {
            "lid": "17",
            "name": "הרצליה",
            "lat": "32.1643",
            "lon": "34.8423",
            "zoom": "3",
            "height": "45",
            "is_park": "0"
        },
        "18": {
            "lid": "18",
            "name": "חדרה",
            "lat": "32.4351",
            "lon": "34.9136",
            "zoom": "2",
            "height": "25",
            "is_park": "0"
        },
        "19": {
            "lid": "19",
            "name": "מודיעין",
            "lat": "31.8960",
            "lon": "35.0199",
            "zoom": "2",
            "height": "270",
            "is_park": "0"
        },
        "20": {
            "lid": "20",
            "name": "רמלה",
            "lat": "31.9308",
            "lon": "34.8686",
            "zoom": "4",
            "height": "80",
            "is_park": "0"
        },
        "21": {
            "lid": "21",
            "name": "רעננה",
            "lat": "32.1807",
            "lon": "34.8709",
            "zoom": "4",
            "height": "50",
            "is_park": "0"
        },
        "22": {
            "lid": "22",
            "name": "מודיעין עילית",
            "lat": "31.9330",
            "lon": "35.0431",
            "zoom": "3",
            "height": "290",
            "is_park": "0"
        },
        "23": {
            "lid": "23",
            "name": "רהט",
            "lat": "31.3921",
            "lon": "34.7581",
            "zoom": "1",
            "height": "230",
            "is_park": "0"
        },
        "24": {
            "lid": "24",
            "name": "הוד השרון",
            "lat": "32.1555",
            "lon": "34.8975",
            "zoom": "5",
            "height": "45",
            "is_park": "0"
        },
        "25": {
            "lid": "25",
            "name": "גבעתיים",
            "lat": "32.0686",
            "lon": "34.8078",
            "zoom": "5",
            "height": "70",
            "is_park": "0"
        },
        "26": {
            "lid": "26",
            "name": "קריית אתא",
            "lat": "32.8051",
            "lon": "35.1056",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "27": {
            "lid": "27",
            "name": "נהריה",
            "lat": "33.0070",
            "lon": "35.0979",
            "zoom": "1",
            "height": "15",
            "is_park": "0"
        },
        "28": {
            "lid": "28",
            "name": "ביתר עילית",
            "lat": "31.6977",
            "lon": "35.1205",
            "zoom": "2",
            "height": "710",
            "is_park": "0"
        },
        "29": {
            "lid": "29",
            "name": "אום אל-פחם",
            "lat": "32.5165",
            "lon": "35.1517",
            "zoom": "1",
            "height": "400",
            "is_park": "0"
        },
        "30": {
            "lid": "30",
            "name": "קריית גת",
            "lat": "31.6086",
            "lon": "34.7718",
            "zoom": "2",
            "height": "125",
            "is_park": "0"
        },
        "31": {
            "lid": "31",
            "name": "אילת",
            "lat": "29.5552",
            "lon": "34.9511",
            "zoom": "1",
            "height": "50",
            "is_park": "0"
        },
        "32": {
            "lid": "32",
            "name": "ראש העין",
            "lat": "32.0970",
            "lon": "34.9443",
            "zoom": "4",
            "height": "50",
            "is_park": "0"
        },
        "33": {
            "lid": "33",
            "name": "עפולה",
            "lat": "32.6094",
            "lon": "35.2901",
            "zoom": "1",
            "height": "80",
            "is_park": "0"
        },
        "34": {
            "lid": "34",
            "name": "נס ציונה",
            "lat": "31.9288",
            "lon": "34.8010",
            "zoom": "4",
            "height": "35",
            "is_park": "0"
        },
        "35": {
            "lid": "35",
            "name": "עכו",
            "lat": "32.9249",
            "lon": "35.0713",
            "zoom": "3",
            "height": "10",
            "is_park": "0"
        },
        "36": {
            "lid": "36",
            "name": "אלעד",
            "lat": "32.0492",
            "lon": "34.9487",
            "zoom": "1",
            "height": "120",
            "is_park": "0"
        },
        "37": {
            "lid": "37",
            "name": "רמת השרון",
            "lat": "32.1436",
            "lon": "34.8435",
            "zoom": "4",
            "height": "45",
            "is_park": "0"
        },
        "38": {
            "lid": "38",
            "name": "כרמיאל",
            "lat": "32.9205",
            "lon": "35.3033",
            "zoom": "1",
            "height": "235",
            "is_park": "0"
        },
        "39": {
            "lid": "39",
            "name": "יבנה",
            "lat": "31.8736",
            "lon": "34.7452",
            "zoom": "3",
            "height": "30",
            "is_park": "0"
        },
        "40": {
            "lid": "40",
            "name": "טבריה",
            "lat": "32.7920",
            "lon": "35.5390",
            "zoom": "1",
            "height": "-200",
            "is_park": "0"
        },
        "41": {
            "lid": "41",
            "name": "טייבה",
            "lat": "32.2693",
            "lon": "35.0054",
            "zoom": "4",
            "height": "70",
            "is_park": "0"
        },
        "42": {
            "lid": "42",
            "name": "קריית מוצקין",
            "lat": "32.8321",
            "lon": "35.0735",
            "zoom": "4",
            "height": "10",
            "is_park": "0"
        },
        "43": {
            "lid": "43",
            "name": "שפרעם",
            "lat": "32.8051",
            "lon": "35.1707",
            "zoom": "4",
            "height": "130",
            "is_park": "0"
        },
        "44": {
            "lid": "44",
            "name": "נוף הגליל",
            "lat": "32.7086",
            "lon": "35.3169",
            "zoom": "5",
            "height": "430",
            "is_park": "0"
        },
        "45": {
            "lid": "45",
            "name": "קריית ים",
            "lat": "32.8438",
            "lon": "35.0671",
            "zoom": "5",
            "height": "10",
            "is_park": "0"
        },
        "46": {
            "lid": "46",
            "name": "קריית ביאליק",
            "lat": "32.8312",
            "lon": "35.0821",
            "zoom": "5",
            "height": "15",
            "is_park": "0"
        },
        "47": {
            "lid": "47",
            "name": "קריית אונו",
            "lat": "32.0598",
            "lon": "34.8554",
            "zoom": "4",
            "height": "65",
            "is_park": "0"
        },
        "48": {
            "lid": "48",
            "name": "מעלה אדומים",
            "lat": "31.7788",
            "lon": "35.2989",
            "zoom": "3",
            "height": "480",
            "is_park": "0"
        },
        "49": {
            "lid": "49",
            "name": "אור יהודה",
            "lat": "32.0300",
            "lon": "34.8460",
            "zoom": "3",
            "height": "30",
            "is_park": "0"
        },
        "50": {
            "lid": "50",
            "name": "צפת",
            "lat": "32.9707",
            "lon": "35.4959",
            "zoom": "1",
            "height": "800",
            "is_park": "0"
        },
        "51": {
            "lid": "51",
            "name": "נתיבות",
            "lat": "31.4257",
            "lon": "34.5949",
            "zoom": "3",
            "height": "150",
            "is_park": "0"
        },
        "52": {
            "lid": "52",
            "name": "דימונה",
            "lat": "31.0654",
            "lon": "35.0320",
            "zoom": "1",
            "height": "550",
            "is_park": "0"
        },
        "53": {
            "lid": "53",
            "name": "טמרה",
            "lat": "32.8511",
            "lon": "35.2070",
            "zoom": "3",
            "height": "120",
            "is_park": "0"
        },
        "54": {
            "lid": "54",
            "name": "סח'נין",
            "lat": "32.8664",
            "lon": "35.2936",
            "zoom": "4",
            "height": "250",
            "is_park": "0"
        },
        "55": {
            "lid": "55",
            "name": "יהוד",
            "lat": "32.0328",
            "lon": "34.8820",
            "zoom": "4",
            "height": "40",
            "is_park": "0"
        },
        "56": {
            "lid": "56",
            "name": "באקה אל גרבייה",
            "lat": "32.4118",
            "lon": "35.0380",
            "zoom": "3",
            "height": "100",
            "is_park": "0"
        },
        "57": {
            "lid": "57",
            "name": "אופקים",
            "lat": "31.3149",
            "lon": "34.6208",
            "zoom": "1",
            "height": "130",
            "is_park": "0"
        },
        "58": {
            "lid": "58",
            "name": "גבעת שמואל",
            "lat": "32.0769",
            "lon": "34.8480",
            "zoom": "5",
            "height": "50",
            "is_park": "0"
        },
        "59": {
            "lid": "59",
            "name": "טירה",
            "lat": "32.2341",
            "lon": "34.9545",
            "zoom": "3",
            "height": "75",
            "is_park": "0"
        },
        "60": {
            "lid": "60",
            "name": "ערד",
            "lat": "31.2558",
            "lon": "35.2122",
            "zoom": "1",
            "height": "600",
            "is_park": "0"
        },
        "61": {
            "lid": "61",
            "name": "מגדל העמק",
            "lat": "32.6780",
            "lon": "35.2390",
            "zoom": "3",
            "height": "220",
            "is_park": "0"
        },
        "62": {
            "lid": "62",
            "name": "שדרות",
            "lat": "31.5240",
            "lon": "34.6006",
            "zoom": "1",
            "height": "90",
            "is_park": "0"
        },
        "63": {
            "lid": "63",
            "name": "עראבה",
            "lat": "32.8510",
            "lon": "35.3384",
            "zoom": "3",
            "height": "250",
            "is_park": "0"
        },
        "64": {
            "lid": "64",
            "name": "נשר",
            "lat": "32.7707",
            "lon": "35.0448",
            "zoom": "3",
            "height": "140",
            "is_park": "0"
        },
        "65": {
            "lid": "65",
            "name": "קריית שמונה",
            "lat": "33.2094",
            "lon": "35.5696",
            "zoom": "1",
            "height": "120",
            "is_park": "0"
        },
        "66": {
            "lid": "66",
            "name": "יקנעם עילית",
            "lat": "32.6599",
            "lon": "35.1100",
            "zoom": "1",
            "height": "140",
            "is_park": "0"
        },
        "67": {
            "lid": "67",
            "name": "כפר קאסם",
            "lat": "32.1142",
            "lon": "34.9771",
            "zoom": "4",
            "height": "140",
            "is_park": "0"
        },
        "68": {
            "lid": "68",
            "name": "כפר יונה",
            "lat": "32.3188",
            "lon": "34.9362",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "69": {
            "lid": "69",
            "name": "קלנסווה",
            "lat": "32.2855",
            "lon": "34.9830",
            "zoom": "1",
            "height": "40",
            "is_park": "0"
        },
        "70": {
            "lid": "70",
            "name": "קריית מלאכי",
            "lat": "31.7320",
            "lon": "34.7406",
            "zoom": "3",
            "height": "65",
            "is_park": "0"
        },
        "71": {
            "lid": "71",
            "name": "מעלות-תרשיחא",
            "lat": "33.0161",
            "lon": "35.2745",
            "zoom": "3",
            "height": "520",
            "is_park": "0"
        },
        "72": {
            "lid": "72",
            "name": "טירת כרמל",
            "lat": "32.7616",
            "lon": "34.9723",
            "zoom": "4",
            "height": "50",
            "is_park": "0"
        },
        "73": {
            "lid": "73",
            "name": "אריאל",
            "lat": "32.1044",
            "lon": "35.1710",
            "zoom": "1",
            "height": "580",
            "is_park": "0"
        },
        "74": {
            "lid": "74",
            "name": "אור עקיבא",
            "lat": "32.5081",
            "lon": "34.9176",
            "zoom": "4",
            "height": "20",
            "is_park": "0"
        },
        "75": {
            "lid": "75",
            "name": "בית שאן",
            "lat": "32.4982",
            "lon": "35.5039",
            "zoom": "2",
            "height": "-130",
            "is_park": "0"
        },
        "76": {
            "lid": "76",
            "name": "מצפה רמון",
            "lat": "30.6095",
            "lon": "34.8011",
            "zoom": "1",
            "height": "860",
            "is_park": "0"
        },
        "77": {
            "lid": "77",
            "name": "לוד",
            "lat": "31.9481",
            "lon": "34.8960",
            "zoom": "4",
            "height": "65",
            "is_park": "0"
        },
        "78": {
            "lid": "78",
            "name": "נצרת",
            "lat": "32.7005",
            "lon": "35.2956",
            "zoom": "1",
            "height": "370",
            "is_park": "0"
        },
        "79": {
            "lid": "79",
            "name": "קצרין",
            "lat": "32.9927",
            "lon": "35.6887",
            "zoom": "2",
            "height": "320",
            "is_park": "0"
        },
        "80": {
            "lid": "80",
            "name": "עין גדי",
            "lat": "31.4664",
            "lon": "35.3880",
            "zoom": "1",
            "height": "-205",
            "is_park": "0"
        },
        "200": {
            "lid": "200",
            "name": "מבצר נמרוד",
            "lat": "33.2524",
            "lon": "35.7130",
            "zoom": "5",
            "height": "750",
            "is_park": "1"
        },
        "201": {
            "lid": "201",
            "name": "נחל חרמון - בניאס",
            "lat": "33.2486",
            "lon": "35.6951",
            "zoom": "1",
            "height": "350",
            "is_park": "1"
        },
        "202": {
            "lid": "202",
            "name": "תל דן",
            "lat": "33.2459",
            "lon": "35.6483",
            "zoom": "3",
            "height": "200",
            "is_park": "1"
        },
        "203": {
            "lid": "203",
            "name": "נחל שניר",
            "lat": "33.2364",
            "lon": "35.6234",
            "zoom": "4",
            "height": "130",
            "is_park": "1"
        },
        "204": {
            "lid": "204",
            "name": "חורשת טל",
            "lat": "33.2191",
            "lon": "35.6322",
            "zoom": "5",
            "height": "150",
            "is_park": "1"
        },
        "205": {
            "lid": "205",
            "name": "נחל עיון",
            "lat": "33.2671",
            "lon": "35.5773",
            "zoom": "4",
            "height": "400",
            "is_park": "1"
        },
        "206": {
            "lid": "206",
            "name": "חולה",
            "lat": "33.0722",
            "lon": "35.5937",
            "zoom": "2",
            "height": "70",
            "is_park": "1"
        },
        "207": {
            "lid": "207",
            "name": "תל חצור",
            "lat": "33.0182",
            "lon": "35.5698",
            "zoom": "4",
            "height": "220",
            "is_park": "1"
        },
        "208": {
            "lid": "208",
            "name": "אכזיב",
            "lat": "33.0488",
            "lon": "35.1019",
            "zoom": "2",
            "height": "10",
            "is_park": "1"
        },
        "209": {
            "lid": "209",
            "name": "מבצר יחיעם",
            "lat": "32.9948",
            "lon": "35.2220",
            "zoom": "4",
            "height": "370",
            "is_park": "1"
        },
        "210": {
            "lid": "210",
            "name": "ברעם",
            "lat": "33.0441",
            "lon": "35.4142",
            "zoom": "2",
            "height": "740",
            "is_park": "1"
        },
        "211": {
            "lid": "211",
            "name": "נחל עמוד",
            "lat": "32.9131",
            "lon": "35.4801",
            "zoom": "3",
            "height": "470",
            "is_park": "1"
        },
        "212": {
            "lid": "212",
            "name": "כורזים",
            "lat": "32.9116",
            "lon": "35.5646",
            "zoom": "4",
            "height": "70",
            "is_park": "1"
        },
        "213": {
            "lid": "213",
            "name": "כפר נחום",
            "lat": "32.8807",
            "lon": "35.5745",
            "zoom": "3",
            "height": "-200",
            "is_park": "1"
        },
        "214": {
            "lid": "214",
            "name": "מג'רסה",
            "lat": "32.8932",
            "lon": "35.6192",
            "zoom": "4",
            "height": "-200",
            "is_park": "1"
        },
        "215": {
            "lid": "215",
            "name": "בריכת המשושים",
            "lat": "32.9371",
            "lon": "35.6611",
            "zoom": "4",
            "height": "30",
            "is_park": "1"
        },
        "216": {
            "lid": "216",
            "name": "יהודיה",
            "lat": "32.9412",
            "lon": "35.7041",
            "zoom": "5",
            "height": "150",
            "is_park": "1"
        },
        "217": {
            "lid": "217",
            "name": "גמלא",
            "lat": "32.9052",
            "lon": "35.7469",
            "zoom": "1",
            "height": "370",
            "is_park": "1"
        },
        "218": {
            "lid": "218",
            "name": "כורסי",
            "lat": "32.8244",
            "lon": "35.6503",
            "zoom": "3",
            "height": "-200",
            "is_park": "1"
        },
        "219": {
            "lid": "219",
            "name": "חמת טבריה",
            "lat": "32.7663",
            "lon": "35.5508",
            "zoom": "4",
            "height": "-200",
            "is_park": "1"
        },
        "220": {
            "lid": "220",
            "name": "ארבל",
            "lat": "32.8224",
            "lon": "35.4960",
            "zoom": "3",
            "height": "100",
            "is_park": "1"
        },
        "221": {
            "lid": "221",
            "name": "עין אפק",
            "lat": "32.8475",
            "lon": "35.1120",
            "zoom": "3",
            "height": "10",
            "is_park": "1"
        },
        "222": {
            "lid": "222",
            "name": "ציפורי",
            "lat": "32.7533",
            "lon": "35.2784",
            "zoom": "2",
            "height": "270",
            "is_park": "1"
        },
        "223": {
            "lid": "223",
            "name": "חי בר כרמל",
            "lat": "32.7541",
            "lon": "35.0169",
            "zoom": "4",
            "height": "350",
            "is_park": "1"
        },
        "224": {
            "lid": "224",
            "name": "פארק הכרמל",
            "lat": "32.7372",
            "lon": "35.0355",
            "zoom": "3",
            "height": "500",
            "is_park": "1"
        },
        "225": {
            "lid": "225",
            "name": "בית שערים",
            "lat": "32.7021",
            "lon": "35.1309",
            "zoom": "4",
            "height": "100",
            "is_park": "1"
        },
        "226": {
            "lid": "226",
            "name": "משמר הכרמל",
            "lat": "32.7255",
            "lon": "35.0131",
            "zoom": "4",
            "height": "320",
            "is_park": "1"
        },
        "227": {
            "lid": "227",
            "name": "נחל מערות",
            "lat": "32.6712",
            "lon": "34.9664",
            "zoom": "3",
            "height": "40",
            "is_park": "1"
        },
        "228": {
            "lid": "228",
            "name": "דור הבונים",
            "lat": "32.6387",
            "lon": "34.9247",
            "zoom": "4",
            "height": "5",
            "is_park": "1"
        },
        "229": {
            "lid": "229",
            "name": "תל מגידו",
            "lat": "32.5839",
            "lon": "35.1852",
            "zoom": "3",
            "height": "160",
            "is_park": "1"
        },
        "230": {
            "lid": "230",
            "name": "כוכב הירדן",
            "lat": "32.5951",
            "lon": "35.5221",
            "zoom": "1",
            "height": "300",
            "is_park": "1"
        },
        "231": {
            "lid": "231",
            "name": "מעיין חרוד",
            "lat": "32.5493",
            "lon": "35.3559",
            "zoom": "2",
            "height": "-10",
            "is_park": "1"
        },
        "232": {
            "lid": "232",
            "name": "בית אלפא",
            "lat": "32.5189",
            "lon": "35.4268",
            "zoom": "3",
            "height": "-75",
            "is_park": "1"
        },
        "233": {
            "lid": "233",
            "name": "גן השלושה",
            "lat": "32.5061",
            "lon": "35.4461",
            "zoom": "4",
            "height": "-100",
            "is_park": "1"
        },
        "235": {
            "lid": "235",
            "name": "נחל תנינים",
            "lat": "32.5449",
            "lon": "34.9154",
            "zoom": "4",
            "height": "10",
            "is_park": "1"
        },
        "236": {
            "lid": "236",
            "name": "קיסריה",
            "lat": "32.4960",
            "lon": "34.8918",
            "zoom": "1",
            "height": "5",
            "is_park": "1"
        },
        "237": {
            "lid": "237",
            "name": "תל דור",
            "lat": "32.6204",
            "lon": "34.9209",
            "zoom": "3",
            "height": "5",
            "is_park": "1"
        },
        "238": {
            "lid": "238",
            "name": "מרכז להצלת צבי ים",
            "lat": "32.4022",
            "lon": "34.8672",
            "zoom": "5",
            "height": "5",
            "is_park": "1"
        },
        "239": {
            "lid": "239",
            "name": "בית ינאי",
            "lat": "32.3872",
            "lon": "34.8648",
            "zoom": "3",
            "height": "10",
            "is_park": "1"
        },
        "240": {
            "lid": "240",
            "name": "אפולוניה",
            "lat": "32.1921",
            "lon": "34.8070",
            "zoom": "2",
            "height": "30",
            "is_park": "1"
        },
        "241": {
            "lid": "241",
            "name": "אפק ירקון",
            "lat": "32.1121",
            "lon": "34.9138",
            "zoom": "2",
            "height": "35",
            "is_park": "1"
        },
        "242": {
            "lid": "242",
            "name": "פלמחים",
            "lat": "31.9295",
            "lon": "34.6989",
            "zoom": "3",
            "height": "5",
            "is_park": "1"
        },
        "243": {
            "lid": "243",
            "name": "קסטל",
            "lat": "31.7964",
            "lon": "35.1446",
            "zoom": "3",
            "height": "780",
            "is_park": "1"
        },
        "244": {
            "lid": "244",
            "name": "עין חמד",
            "lat": "31.7968",
            "lon": "35.1259",
            "zoom": "5",
            "height": "600",
            "is_park": "1"
        },
        "245": {
            "lid": "245",
            "name": "עיר דויד",
            "lat": "31.7745",
            "lon": "35.2372",
            "zoom": "5",
            "height": "700",
            "is_park": "1"
        },
        "246": {
            "lid": "246",
            "name": "מערת הנטיפים",
            "lat": "31.7556",
            "lon": "35.0214",
            "zoom": "5",
            "height": "420",
            "is_park": "1"
        },
        "248": {
            "lid": "248",
            "name": "בית גוברין",
            "lat": "31.6055",
            "lon": "34.8968",
            "zoom": "1",
            "height": "280",
            "is_park": "1"
        },
        "249": {
            "lid": "249",
            "name": "שחר הגיא",
            "lat": "31.8148",
            "lon": "35.0237",
            "zoom": "3",
            "height": "300",
            "is_park": "1"
        },
        "250": {
            "lid": "250",
            "name": "מגדל צדק",
            "lat": "32.0811",
            "lon": "34.9572",
            "zoom": "4",
            "height": "110",
            "is_park": "1"
        },
        "251": {
            "lid": "251",
            "name": "עין חניה",
            "lat": "31.7439",
            "lon": "35.1561",
            "zoom": "4",
            "height": "620",
            "is_park": "1"
        },
        "252": {
            "lid": "252",
            "name": "סבסטיה",
            "lat": "32.2763",
            "lon": "35.1897",
            "zoom": "1",
            "height": "440",
            "is_park": "1"
        },
        "253": {
            "lid": "253",
            "name": "הר גריזים",
            "lat": "32.1991",
            "lon": "35.2729",
            "zoom": "1",
            "height": "875",
            "is_park": "1"
        },
        "254": {
            "lid": "254",
            "name": "נבי סמואל",
            "lat": "31.8329",
            "lon": "35.1815",
            "zoom": "2",
            "height": "875",
            "is_park": "1"
        },
        "255": {
            "lid": "255",
            "name": "עין פרת",
            "lat": "31.8323",
            "lon": "35.3048",
            "zoom": "3",
            "height": "280",
            "is_park": "1"
        },
        "256": {
            "lid": "256",
            "name": "עין מבוע",
            "lat": "31.8399",
            "lon": "35.3493",
            "zoom": "5",
            "height": "100",
            "is_park": "1"
        },
        "257": {
            "lid": "257",
            "name": "קאסר אל-יהוד",
            "lat": "31.8413",
            "lon": "35.5286",
            "zoom": "1",
            "height": "-385",
            "is_park": "1"
        },
        "258": {
            "lid": "258",
            "name": "אכסניית השומרוני הטוב",
            "lat": "31.8165",
            "lon": "35.3589",
            "zoom": "4",
            "height": "270",
            "is_park": "1"
        },
        "259": {
            "lid": "259",
            "name": "מנזר אותימיוס",
            "lat": "31.7922",
            "lon": "35.3363",
            "zoom": "4",
            "height": "230",
            "is_park": "1"
        },
        "261": {
            "lid": "261",
            "name": "קומראן",
            "lat": "31.7419",
            "lon": "35.4622",
            "zoom": "2",
            "height": "-330",
            "is_park": "1"
        },
        "262": {
            "lid": "262",
            "name": "עיינות צוקים",
            "lat": "31.7170",
            "lon": "35.4526",
            "zoom": "3",
            "height": "-390",
            "is_park": "1"
        },
        "263": {
            "lid": "263",
            "name": "הרודיון",
            "lat": "31.6650",
            "lon": "35.2412",
            "zoom": "2",
            "height": "740",
            "is_park": "1"
        },
        "264": {
            "lid": "264",
            "name": "תל חברון",
            "lat": "31.5244",
            "lon": "35.1008",
            "zoom": "2",
            "height": "925",
            "is_park": "1"
        },
        "267": {
            "lid": "267",
            "name": "מצדה",
            "lat": "31.3125",
            "lon": "35.3635",
            "zoom": "1",
            "height": "50",
            "is_park": "1"
        },
        "268": {
            "lid": "268",
            "name": "תל ערד",
            "lat": "31.2776",
            "lon": "35.1258",
            "zoom": "3",
            "height": "560",
            "is_park": "1"
        },
        "269": {
            "lid": "269",
            "name": "תל באר שבע",
            "lat": "31.2453",
            "lon": "34.8403",
            "zoom": "5",
            "height": "300",
            "is_park": "1"
        },
        "270": {
            "lid": "270",
            "name": "אשכול",
            "lat": "31.3091",
            "lon": "34.4926",
            "zoom": "1",
            "height": "70",
            "is_park": "1"
        },
        "271": {
            "lid": "271",
            "name": "ממשית",
            "lat": "31.0256",
            "lon": "35.0651",
            "zoom": "2",
            "height": "470",
            "is_park": "1"
        },
        "272": {
            "lid": "272",
            "name": "שבטה",
            "lat": "30.8808",
            "lon": "34.6289",
            "zoom": "2",
            "height": "350",
            "is_park": "1"
        },
        "273": {
            "lid": "273",
            "name": "קבר בן גוריון",
            "lat": "30.8483",
            "lon": "34.7820",
            "zoom": "3",
            "height": "475",
            "is_park": "1"
        },
        "274": {
            "lid": "274",
            "name": "עין עבדת",
            "lat": "30.8237",
            "lon": "34.7612",
            "zoom": "4",
            "height": "400",
            "is_park": "1"
        },
        "275": {
            "lid": "275",
            "name": "עבדת",
            "lat": "30.7927",
            "lon": "34.7749",
            "zoom": "1",
            "height": "600",
            "is_park": "1"
        },
        "277": {
            "lid": "277",
            "name": "חי בר יטבתה",
            "lat": "29.8691",
            "lon": "35.0430",
            "zoom": "1",
            "height": "65",
            "is_park": "1"
        },
        "278": {
            "lid": "278",
            "name": "חוף האלמוגים",
            "lat": "29.5082",
            "lon": "34.9214",
            "zoom": "4",
            "height": "0",
            "is_park": "1"
        }
    }

        EN_LOCATIONS = {
        "1": {
            "lid": "1",
            "name": "Jerusalem",
            "lat": "31.7780",
            "lon": "35.2000",
            "zoom": "1",
            "height": "780",
            "is_park": "0"
        },
        "2": {
            "lid": "2",
            "name": "Tel Aviv - Yafo",
            "lat": "32.0821",
            "lon": "34.7802",
            "zoom": "1",
            "height": "30",
            "is_park": "0"
        },
        "3": {
            "lid": "3",
            "name": "Haifa",
            "lat": "32.7900",
            "lon": "34.9900",
            "zoom": "1",
            "height": "250",
            "is_park": "0"
        },
        "4": {
            "lid": "4",
            "name": "Rishon le Zion",
            "lat": "31.9640",
            "lon": "34.8040",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "5": {
            "lid": "5",
            "name": "Petah Tiqva",
            "lat": "32.0869",
            "lon": "34.8882",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "6": {
            "lid": "6",
            "name": "Ashdod",
            "lat": "31.8011",
            "lon": "34.6410",
            "zoom": "1",
            "height": "30",
            "is_park": "0"
        },
        "7": {
            "lid": "7",
            "name": "Netania",
            "lat": "32.3285",
            "lon": "34.8565",
            "zoom": "1",
            "height": "35",
            "is_park": "0"
        },
        "8": {
            "lid": "8",
            "name": "Beer Sheva",
            "lat": "31.2497",
            "lon": "34.7997",
            "zoom": "1",
            "height": "280",
            "is_park": "0"
        },
        "9": {
            "lid": "9",
            "name": "Bnei Brak",
            "lat": "32.0868",
            "lon": "34.8363",
            "zoom": "5",
            "height": "35",
            "is_park": "0"
        },
        "10": {
            "lid": "10",
            "name": "Holon",
            "lat": "32.0171",
            "lon": "34.7688",
            "zoom": "4",
            "height": "35",
            "is_park": "0"
        },
        "11": {
            "lid": "11",
            "name": "Ramat Gan",
            "lat": "32.0822",
            "lon": "34.8141",
            "zoom": "4",
            "height": "50",
            "is_park": "0"
        },
        "12": {
            "lid": "12",
            "name": "Asheqelon",
            "lat": "31.6654",
            "lon": "34.5638",
            "zoom": "1",
            "height": "40",
            "is_park": "0"
        },
        "13": {
            "lid": "13",
            "name": "Rehovot",
            "lat": "31.8982",
            "lon": "34.8085",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "14": {
            "lid": "14",
            "name": "Bat Yam",
            "lat": "32.0161",
            "lon": "34.7413",
            "zoom": "3",
            "height": "20",
            "is_park": "0"
        },
        "15": {
            "lid": "15",
            "name": "Bet Shemesh",
            "lat": "31.7498",
            "lon": "34.9864",
            "zoom": "3",
            "height": "300",
            "is_park": "0"
        },
        "16": {
            "lid": "16",
            "name": "Kfar Sava",
            "lat": "32.1726",
            "lon": "34.9080",
            "zoom": "3",
            "height": "55",
            "is_park": "0"
        },
        "17": {
            "lid": "17",
            "name": "Herzliya",
            "lat": "32.1643",
            "lon": "34.8423",
            "zoom": "3",
            "height": "45",
            "is_park": "0"
        },
        "18": {
            "lid": "18",
            "name": "Hadera",
            "lat": "32.4351",
            "lon": "34.9136",
            "zoom": "2",
            "height": "25",
            "is_park": "0"
        },
        "19": {
            "lid": "19",
            "name": "Modiin",
            "lat": "31.8960",
            "lon": "35.0199",
            "zoom": "2",
            "height": "270",
            "is_park": "0"
        },
        "20": {
            "lid": "20",
            "name": "Ramla",
            "lat": "31.9308",
            "lon": "34.8686",
            "zoom": "4",
            "height": "80",
            "is_park": "0"
        },
        "21": {
            "lid": "21",
            "name": "Raanana",
            "lat": "32.1807",
            "lon": "34.8709",
            "zoom": "4",
            "height": "50",
            "is_park": "0"
        },
        "22": {
            "lid": "22",
            "name": "Modiin Illit",
            "lat": "31.9330",
            "lon": "35.0431",
            "zoom": "3",
            "height": "290",
            "is_park": "0"
        },
        "23": {
            "lid": "23",
            "name": "Rahat",
            "lat": "31.3921",
            "lon": "34.7581",
            "zoom": "1",
            "height": "230",
            "is_park": "0"
        },
        "24": {
            "lid": "24",
            "name": "Hod Hasharon",
            "lat": "32.1555",
            "lon": "34.8975",
            "zoom": "5",
            "height": "45",
            "is_park": "0"
        },
        "25": {
            "lid": "25",
            "name": "Givatayim",
            "lat": "32.0686",
            "lon": "34.8078",
            "zoom": "5",
            "height": "70",
            "is_park": "0"
        },
        "26": {
            "lid": "26",
            "name": "Kiryat Ata",
            "lat": "32.8051",
            "lon": "35.1056",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "27": {
            "lid": "27",
            "name": "Nahariya",
            "lat": "33.0070",
            "lon": "35.0979",
            "zoom": "1",
            "height": "15",
            "is_park": "0"
        },
        "28": {
            "lid": "28",
            "name": "Beitar Illit",
            "lat": "31.6977",
            "lon": "35.1205",
            "zoom": "2",
            "height": "710",
            "is_park": "0"
        },
        "29": {
            "lid": "29",
            "name": "Um al-Fahm",
            "lat": "32.5165",
            "lon": "35.1517",
            "zoom": "1",
            "height": "400",
            "is_park": "0"
        },
        "30": {
            "lid": "30",
            "name": "Kiryat Gat",
            "lat": "31.6086",
            "lon": "34.7718",
            "zoom": "2",
            "height": "125",
            "is_park": "0"
        },
        "31": {
            "lid": "31",
            "name": "Eilat",
            "lat": "29.5552",
            "lon": "34.9511",
            "zoom": "1",
            "height": "50",
            "is_park": "0"
        },
        "32": {
            "lid": "32",
            "name": "Rosh Haayin",
            "lat": "32.0970",
            "lon": "34.9443",
            "zoom": "4",
            "height": "50",
            "is_park": "0"
        },
        "33": {
            "lid": "33",
            "name": "Afula",
            "lat": "32.6094",
            "lon": "35.2901",
            "zoom": "1",
            "height": "80",
            "is_park": "0"
        },
        "34": {
            "lid": "34",
            "name": "Nes-Ziona",
            "lat": "31.9288",
            "lon": "34.8010",
            "zoom": "4",
            "height": "35",
            "is_park": "0"
        },
        "35": {
            "lid": "35",
            "name": "Akko",
            "lat": "32.9249",
            "lon": "35.0713",
            "zoom": "3",
            "height": "10",
            "is_park": "0"
        },
        "36": {
            "lid": "36",
            "name": "Elad",
            "lat": "32.0492",
            "lon": "34.9487",
            "zoom": "1",
            "height": "120",
            "is_park": "0"
        },
        "37": {
            "lid": "37",
            "name": "Ramat Hasharon",
            "lat": "32.1436",
            "lon": "34.8435",
            "zoom": "4",
            "height": "45",
            "is_park": "0"
        },
        "38": {
            "lid": "38",
            "name": "Karmiel",
            "lat": "32.9205",
            "lon": "35.3033",
            "zoom": "1",
            "height": "235",
            "is_park": "0"
        },
        "39": {
            "lid": "39",
            "name": "Yavneh",
            "lat": "31.8736",
            "lon": "34.7452",
            "zoom": "3",
            "height": "30",
            "is_park": "0"
        },
        "40": {
            "lid": "40",
            "name": "Tiberias",
            "lat": "32.7920",
            "lon": "35.5390",
            "zoom": "1",
            "height": "-200",
            "is_park": "0"
        },
        "41": {
            "lid": "41",
            "name": "Tayibe",
            "lat": "32.2693",
            "lon": "35.0054",
            "zoom": "4",
            "height": "70",
            "is_park": "0"
        },
        "42": {
            "lid": "42",
            "name": "Kiryat Motzkin",
            "lat": "32.8321",
            "lon": "35.0735",
            "zoom": "4",
            "height": "10",
            "is_park": "0"
        },
        "43": {
            "lid": "43",
            "name": "Shfaram",
            "lat": "32.8051",
            "lon": "35.1707",
            "zoom": "4",
            "height": "130",
            "is_park": "0"
        },
        "44": {
            "lid": "44",
            "name": "Nof Hagalil",
            "lat": "32.7086",
            "lon": "35.3169",
            "zoom": "5",
            "height": "430",
            "is_park": "0"
        },
        "45": {
            "lid": "45",
            "name": "Kiryat Yam",
            "lat": "32.8438",
            "lon": "35.0671",
            "zoom": "5",
            "height": "10",
            "is_park": "0"
        },
        "46": {
            "lid": "46",
            "name": "Kiryat Bialik",
            "lat": "32.8312",
            "lon": "35.0821",
            "zoom": "5",
            "height": "15",
            "is_park": "0"
        },
        "47": {
            "lid": "47",
            "name": "Kiryat Ono",
            "lat": "32.0598",
            "lon": "34.8554",
            "zoom": "4",
            "height": "65",
            "is_park": "0"
        },
        "48": {
            "lid": "48",
            "name": "Maale Adumim",
            "lat": "31.7788",
            "lon": "35.2989",
            "zoom": "3",
            "height": "480",
            "is_park": "0"
        },
        "49": {
            "lid": "49",
            "name": "Or Yehuda",
            "lat": "32.0300",
            "lon": "34.8460",
            "zoom": "3",
            "height": "30",
            "is_park": "0"
        },
        "50": {
            "lid": "50",
            "name": "Zefat",
            "lat": "32.9707",
            "lon": "35.4959",
            "zoom": "1",
            "height": "800",
            "is_park": "0"
        },
        "51": {
            "lid": "51",
            "name": "Netivot",
            "lat": "31.4257",
            "lon": "34.5949",
            "zoom": "3",
            "height": "150",
            "is_park": "0"
        },
        "52": {
            "lid": "52",
            "name": "Dimona",
            "lat": "31.0654",
            "lon": "35.0320",
            "zoom": "1",
            "height": "550",
            "is_park": "0"
        },
        "53": {
            "lid": "53",
            "name": "Tamra ",
            "lat": "32.8511",
            "lon": "35.2070",
            "zoom": "3",
            "height": "120",
            "is_park": "0"
        },
        "54": {
            "lid": "54",
            "name": "Sakhnin",
            "lat": "32.8664",
            "lon": "35.2936",
            "zoom": "4",
            "height": "250",
            "is_park": "0"
        },
        "55": {
            "lid": "55",
            "name": "Yehud",
            "lat": "32.0328",
            "lon": "34.8820",
            "zoom": "4",
            "height": "40",
            "is_park": "0"
        },
        "56": {
            "lid": "56",
            "name": "Baka al-Gharbiya",
            "lat": "32.4118",
            "lon": "35.0380",
            "zoom": "3",
            "height": "100",
            "is_park": "0"
        },
        "57": {
            "lid": "57",
            "name": "Ofakim",
            "lat": "31.3149",
            "lon": "34.6208",
            "zoom": "1",
            "height": "130",
            "is_park": "0"
        },
        "58": {
            "lid": "58",
            "name": "Givat Shmuel",
            "lat": "32.0769",
            "lon": "34.8480",
            "zoom": "5",
            "height": "50",
            "is_park": "0"
        },
        "59": {
            "lid": "59",
            "name": "Tira",
            "lat": "32.2341",
            "lon": "34.9545",
            "zoom": "3",
            "height": "75",
            "is_park": "0"
        },
        "60": {
            "lid": "60",
            "name": "Arad",
            "lat": "31.2558",
            "lon": "35.2122",
            "zoom": "1",
            "height": "600",
            "is_park": "0"
        },
        "61": {
            "lid": "61",
            "name": "Migdal Haemek",
            "lat": "32.6780",
            "lon": "35.2390",
            "zoom": "3",
            "height": "220",
            "is_park": "0"
        },
        "62": {
            "lid": "62",
            "name": "Sderot",
            "lat": "31.5240",
            "lon": "34.6006",
            "zoom": "1",
            "height": "90",
            "is_park": "0"
        },
        "63": {
            "lid": "63",
            "name": "Araba",
            "lat": "32.8510",
            "lon": "35.3384",
            "zoom": "3",
            "height": "250",
            "is_park": "0"
        },
        "64": {
            "lid": "64",
            "name": "Nesher",
            "lat": "32.7707",
            "lon": "35.0448",
            "zoom": "3",
            "height": "140",
            "is_park": "0"
        },
        "65": {
            "lid": "65",
            "name": "Kiryat Shmona",
            "lat": "33.2094",
            "lon": "35.5696",
            "zoom": "1",
            "height": "120",
            "is_park": "0"
        },
        "66": {
            "lid": "66",
            "name": "Yokneam Illit",
            "lat": "32.6599",
            "lon": "35.1100",
            "zoom": "1",
            "height": "140",
            "is_park": "0"
        },
        "67": {
            "lid": "67",
            "name": "Kafr Qassem",
            "lat": "32.1142",
            "lon": "34.9771",
            "zoom": "4",
            "height": "140",
            "is_park": "0"
        },
        "68": {
            "lid": "68",
            "name": "Kfar Yona",
            "lat": "32.3188",
            "lon": "34.9362",
            "zoom": "3",
            "height": "50",
            "is_park": "0"
        },
        "69": {
            "lid": "69",
            "name": "Qalansawa",
            "lat": "32.2855",
            "lon": "34.9830",
            "zoom": "1",
            "height": "40",
            "is_park": "0"
        },
        "70": {
            "lid": "70",
            "name": "Kiryat Malachi",
            "lat": "31.7320",
            "lon": "34.7406",
            "zoom": "3",
            "height": "65",
            "is_park": "0"
        },
        "71": {
            "lid": "71",
            "name": "Maalot-Tarshiha",
            "lat": "33.0161",
            "lon": "35.2745",
            "zoom": "3",
            "height": "520",
            "is_park": "0"
        },
        "72": {
            "lid": "72",
            "name": "Tirat Carmel",
            "lat": "32.7616",
            "lon": "34.9723",
            "zoom": "4",
            "height": "50",
            "is_park": "0"
        },
        "73": {
            "lid": "73",
            "name": "Ariel",
            "lat": "32.1044",
            "lon": "35.1710",
            "zoom": "1",
            "height": "580",
            "is_park": "0"
        },
        "74": {
            "lid": "74",
            "name": "Or Akiva",
            "lat": "32.5081",
            "lon": "34.9176",
            "zoom": "4",
            "height": "20",
            "is_park": "0"
        },
        "75": {
            "lid": "75",
            "name": "Bet Shean",
            "lat": "32.4982",
            "lon": "35.5039",
            "zoom": "2",
            "height": "-130",
            "is_park": "0"
        },
        "76": {
            "lid": "76",
            "name": "Mizpe Ramon",
            "lat": "30.6095",
            "lon": "34.8011",
            "zoom": "1",
            "height": "860",
            "is_park": "0"
        },
        "77": {
            "lid": "77",
            "name": "Lod",
            "lat": "31.9481",
            "lon": "34.8960",
            "zoom": "4",
            "height": "65",
            "is_park": "0"
        },
        "78": {
            "lid": "78",
            "name": "Nazareth",
            "lat": "32.7005",
            "lon": "35.2956",
            "zoom": "1",
            "height": "370",
            "is_park": "0"
        },
        "79": {
            "lid": "79",
            "name": "Qazrin",
            "lat": "32.9927",
            "lon": "35.6887",
            "zoom": "2",
            "height": "320",
            "is_park": "0"
        },
        "80": {
            "lid": "80",
            "name": "En Gedi",
            "lat": "31.4664",
            "lon": "35.3880",
            "zoom": "1",
            "height": "-205",
            "is_park": "0"
        },
        "200": {
            "lid": "200",
            "name": "Nimrod Fortress",
            "lat": "33.2524",
            "lon": "35.7130",
            "zoom": "5",
            "height": "750",
            "is_park": "1"
        },
        "201": {
            "lid": "201",
            "name": "Banias",
            "lat": "33.2486",
            "lon": "35.6951",
            "zoom": "1",
            "height": "350",
            "is_park": "1"
        },
        "202": {
            "lid": "202",
            "name": "Tel Dan",
            "lat": "33.2459",
            "lon": "35.6483",
            "zoom": "3",
            "height": "200",
            "is_park": "1"
        },
        "203": {
            "lid": "203",
            "name": "Snir Stream",
            "lat": "33.2364",
            "lon": "35.6234",
            "zoom": "4",
            "height": "130",
            "is_park": "1"
        },
        "204": {
            "lid": "204",
            "name": "Horshat Tal ",
            "lat": "33.2191",
            "lon": "35.6322",
            "zoom": "5",
            "height": "150",
            "is_park": "1"
        },
        "205": {
            "lid": "205",
            "name": "Ayun Stream",
            "lat": "33.2671",
            "lon": "35.5773",
            "zoom": "4",
            "height": "400",
            "is_park": "1"
        },
        "206": {
            "lid": "206",
            "name": "Hula",
            "lat": "33.0722",
            "lon": "35.5937",
            "zoom": "2",
            "height": "70",
            "is_park": "1"
        },
        "207": {
            "lid": "207",
            "name": "Tel Hazor",
            "lat": "33.0182",
            "lon": "35.5698",
            "zoom": "4",
            "height": "220",
            "is_park": "1"
        },
        "208": {
            "lid": "208",
            "name": "Akhziv",
            "lat": "33.0488",
            "lon": "35.1019",
            "zoom": "2",
            "height": "10",
            "is_park": "1"
        },
        "209": {
            "lid": "209",
            "name": "Yehiam Fortress",
            "lat": "32.9948",
            "lon": "35.2220",
            "zoom": "4",
            "height": "370",
            "is_park": "1"
        },
        "210": {
            "lid": "210",
            "name": "Baram",
            "lat": "33.0441",
            "lon": "35.4142",
            "zoom": "2",
            "height": "740",
            "is_park": "1"
        },
        "211": {
            "lid": "211",
            "name": "Amud Stream",
            "lat": "32.9131",
            "lon": "35.4801",
            "zoom": "3",
            "height": "470",
            "is_park": "1"
        },
        "212": {
            "lid": "212",
            "name": "Korazim",
            "lat": "32.9116",
            "lon": "35.5646",
            "zoom": "4",
            "height": "70",
            "is_park": "1"
        },
        "213": {
            "lid": "213",
            "name": "Kfar Nahum",
            "lat": "32.8807",
            "lon": "35.5745",
            "zoom": "3",
            "height": "-200",
            "is_park": "1"
        },
        "214": {
            "lid": "214",
            "name": "Majrase ",
            "lat": "32.8932",
            "lon": "35.6192",
            "zoom": "4",
            "height": "-200",
            "is_park": "1"
        },
        "215": {
            "lid": "215",
            "name": "Meshushim Stream",
            "lat": "32.9371",
            "lon": "35.6611",
            "zoom": "4",
            "height": "30",
            "is_park": "1"
        },
        "216": {
            "lid": "216",
            "name": "Yehudiya ",
            "lat": "32.9412",
            "lon": "35.7041",
            "zoom": "5",
            "height": "150",
            "is_park": "1"
        },
        "217": {
            "lid": "217",
            "name": "Gamla",
            "lat": "32.9052",
            "lon": "35.7469",
            "zoom": "1",
            "height": "370",
            "is_park": "1"
        },
        "218": {
            "lid": "218",
            "name": "Kursi ",
            "lat": "32.8244",
            "lon": "35.6503",
            "zoom": "3",
            "height": "-200",
            "is_park": "1"
        },
        "219": {
            "lid": "219",
            "name": "Hamat Tiberias",
            "lat": "32.7663",
            "lon": "35.5508",
            "zoom": "4",
            "height": "-200",
            "is_park": "1"
        },
        "220": {
            "lid": "220",
            "name": "Arbel",
            "lat": "32.8224",
            "lon": "35.4960",
            "zoom": "3",
            "height": "100",
            "is_park": "1"
        },
        "221": {
            "lid": "221",
            "name": "En Afek",
            "lat": "32.8475",
            "lon": "35.1120",
            "zoom": "3",
            "height": "10",
            "is_park": "1"
        },
        "222": {
            "lid": "222",
            "name": "Tzipori",
            "lat": "32.7533",
            "lon": "35.2784",
            "zoom": "2",
            "height": "270",
            "is_park": "1"
        },
        "223": {
            "lid": "223",
            "name": "Hai-Bar Carmel",
            "lat": "32.7541",
            "lon": "35.0169",
            "zoom": "4",
            "height": "350",
            "is_park": "1"
        },
        "224": {
            "lid": "224",
            "name": "Mount Carmel",
            "lat": "32.7372",
            "lon": "35.0355",
            "zoom": "3",
            "height": "500",
            "is_park": "1"
        },
        "225": {
            "lid": "225",
            "name": "Bet Shearim",
            "lat": "32.7021",
            "lon": "35.1309",
            "zoom": "4",
            "height": "100",
            "is_park": "1"
        },
        "226": {
            "lid": "226",
            "name": "Mishmar HaCarmel ",
            "lat": "32.7255",
            "lon": "35.0131",
            "zoom": "4",
            "height": "320",
            "is_park": "1"
        },
        "227": {
            "lid": "227",
            "name": "Nahal Me‘arot",
            "lat": "32.6712",
            "lon": "34.9664",
            "zoom": "3",
            "height": "40",
            "is_park": "1"
        },
        "228": {
            "lid": "228",
            "name": "Dor-HaBonim",
            "lat": "32.6387",
            "lon": "34.9247",
            "zoom": "4",
            "height": "5",
            "is_park": "1"
        },
        "229": {
            "lid": "229",
            "name": "Tel Megiddo",
            "lat": "32.5839",
            "lon": "35.1852",
            "zoom": "3",
            "height": "160",
            "is_park": "1"
        },
        "230": {
            "lid": "230",
            "name": "Kokhav HaYarden",
            "lat": "32.5951",
            "lon": "35.5221",
            "zoom": "1",
            "height": "300",
            "is_park": "1"
        },
        "231": {
            "lid": "231",
            "name": "Maayan Harod",
            "lat": "32.5493",
            "lon": "35.3559",
            "zoom": "2",
            "height": "-10",
            "is_park": "1"
        },
        "232": {
            "lid": "232",
            "name": "Bet Alpha",
            "lat": "32.5189",
            "lon": "35.4268",
            "zoom": "3",
            "height": "-75",
            "is_park": "1"
        },
        "233": {
            "lid": "233",
            "name": "Gan HaShlosha",
            "lat": "32.5061",
            "lon": "35.4461",
            "zoom": "4",
            "height": "-100",
            "is_park": "1"
        },
        "235": {
            "lid": "235",
            "name": "Taninim Stream",
            "lat": "32.5449",
            "lon": "34.9154",
            "zoom": "4",
            "height": "10",
            "is_park": "1"
        },
        "236": {
            "lid": "236",
            "name": "Caesarea",
            "lat": "32.4960",
            "lon": "34.8918",
            "zoom": "1",
            "height": "5",
            "is_park": "1"
        },
        "237": {
            "lid": "237",
            "name": "Tel Dor",
            "lat": "32.6204",
            "lon": "34.9209",
            "zoom": "3",
            "height": "5",
            "is_park": "1"
        },
        "238": {
            "lid": "238",
            "name": "Mikhmoret Sea Turtle",
            "lat": "32.4022",
            "lon": "34.8672",
            "zoom": "5",
            "height": "5",
            "is_park": "1"
        },
        "239": {
            "lid": "239",
            "name": "Beit Yanai",
            "lat": "32.3872",
            "lon": "34.8648",
            "zoom": "3",
            "height": "10",
            "is_park": "1"
        },
        "240": {
            "lid": "240",
            "name": "Apollonia",
            "lat": "32.1921",
            "lon": "34.8070",
            "zoom": "2",
            "height": "30",
            "is_park": "1"
        },
        "241": {
            "lid": "241",
            "name": "Mekorot HaYarkon",
            "lat": "32.1121",
            "lon": "34.9138",
            "zoom": "2",
            "height": "35",
            "is_park": "1"
        },
        "242": {
            "lid": "242",
            "name": "Palmahim",
            "lat": "31.9295",
            "lon": "34.6989",
            "zoom": "3",
            "height": "5",
            "is_park": "1"
        },
        "243": {
            "lid": "243",
            "name": "Castel",
            "lat": "31.7964",
            "lon": "35.1446",
            "zoom": "3",
            "height": "780",
            "is_park": "1"
        },
        "244": {
            "lid": "244",
            "name": "En Hemed",
            "lat": "31.7968",
            "lon": "35.1259",
            "zoom": "5",
            "height": "600",
            "is_park": "1"
        },
        "245": {
            "lid": "245",
            "name": "City of David",
            "lat": "31.7745",
            "lon": "35.2372",
            "zoom": "5",
            "height": "700",
            "is_park": "1"
        },
        "246": {
            "lid": "246",
            "name": "Me‘arat Soreq",
            "lat": "31.7556",
            "lon": "35.0214",
            "zoom": "5",
            "height": "420",
            "is_park": "1"
        },
        "248": {
            "lid": "248",
            "name": "Bet Guvrin",
            "lat": "31.6055",
            "lon": "34.8968",
            "zoom": "1",
            "height": "280",
            "is_park": "1"
        },
        "249": {
            "lid": "249",
            "name": "Sha’ar HaGai",
            "lat": "31.8148",
            "lon": "35.0237",
            "zoom": "3",
            "height": "300",
            "is_park": "1"
        },
        "250": {
            "lid": "250",
            "name": "Migdal Tsedek",
            "lat": "32.0811",
            "lon": "34.9572",
            "zoom": "4",
            "height": "110",
            "is_park": "1"
        },
        "251": {
            "lid": "251",
            "name": "Haniya Spring",
            "lat": "31.7439",
            "lon": "35.1561",
            "zoom": "4",
            "height": "620",
            "is_park": "1"
        },
        "252": {
            "lid": "252",
            "name": "Sebastia",
            "lat": "32.2763",
            "lon": "35.1897",
            "zoom": "1",
            "height": "440",
            "is_park": "1"
        },
        "253": {
            "lid": "253",
            "name": "Mount Gerizim",
            "lat": "32.1991",
            "lon": "35.2729",
            "zoom": "1",
            "height": "875",
            "is_park": "1"
        },
        "254": {
            "lid": "254",
            "name": "Nebi Samuel",
            "lat": "31.8329",
            "lon": "35.1815",
            "zoom": "2",
            "height": "875",
            "is_park": "1"
        },
        "255": {
            "lid": "255",
            "name": "En Prat",
            "lat": "31.8323",
            "lon": "35.3048",
            "zoom": "3",
            "height": "280",
            "is_park": "1"
        },
        "256": {
            "lid": "256",
            "name": "En Mabo‘a",
            "lat": "31.8399",
            "lon": "35.3493",
            "zoom": "5",
            "height": "100",
            "is_park": "1"
        },
        "257": {
            "lid": "257",
            "name": "Qasr al-Yahud",
            "lat": "31.8413",
            "lon": "35.5286",
            "zoom": "1",
            "height": "-385",
            "is_park": "1"
        },
        "258": {
            "lid": "258",
            "name": "Good Samaritan",
            "lat": "31.8165",
            "lon": "35.3589",
            "zoom": "4",
            "height": "270",
            "is_park": "1"
        },
        "259": {
            "lid": "259",
            "name": "Euthymius Monastery",
            "lat": "31.7922",
            "lon": "35.3363",
            "zoom": "4",
            "height": "230",
            "is_park": "1"
        },
        "261": {
            "lid": "261",
            "name": "Qumran",
            "lat": "31.7419",
            "lon": "35.4622",
            "zoom": "2",
            "height": "-330",
            "is_park": "1"
        },
        "262": {
            "lid": "262",
            "name": "Enot Tsukim",
            "lat": "31.7170",
            "lon": "35.4526",
            "zoom": "3",
            "height": "-390",
            "is_park": "1"
        },
        "263": {
            "lid": "263",
            "name": "Herodium",
            "lat": "31.6650",
            "lon": "35.2412",
            "zoom": "2",
            "height": "740",
            "is_park": "1"
        },
        "264": {
            "lid": "264",
            "name": "Tel Hebron",
            "lat": "31.5244",
            "lon": "35.1008",
            "zoom": "2",
            "height": "925",
            "is_park": "1"
        },
        "267": {
            "lid": "267",
            "name": "Masada ",
            "lat": "31.3125",
            "lon": "35.3635",
            "zoom": "1",
            "height": "50",
            "is_park": "1"
        },
        "268": {
            "lid": "268",
            "name": "Tel Arad",
            "lat": "31.2776",
            "lon": "35.1258",
            "zoom": "3",
            "height": "560",
            "is_park": "1"
        },
        "269": {
            "lid": "269",
            "name": "Tel Beer Sheva",
            "lat": "31.2453",
            "lon": "34.8403",
            "zoom": "5",
            "height": "300",
            "is_park": "1"
        },
        "270": {
            "lid": "270",
            "name": "Eshkol",
            "lat": "31.3091",
            "lon": "34.4926",
            "zoom": "1",
            "height": "70",
            "is_park": "1"
        },
        "271": {
            "lid": "271",
            "name": "Mamshit",
            "lat": "31.0256",
            "lon": "35.0651",
            "zoom": "2",
            "height": "470",
            "is_park": "1"
        },
        "272": {
            "lid": "272",
            "name": "Shivta",
            "lat": "30.8808",
            "lon": "34.6289",
            "zoom": "2",
            "height": "350",
            "is_park": "1"
        },
        "273": {
            "lid": "273",
            "name": "Ben-Gurion’s Tomb",
            "lat": "30.8483",
            "lon": "34.7820",
            "zoom": "3",
            "height": "475",
            "is_park": "1"
        },
        "274": {
            "lid": "274",
            "name": "En Avdat",
            "lat": "30.8237",
            "lon": "34.7612",
            "zoom": "4",
            "height": "400",
            "is_park": "1"
        },
        "275": {
            "lid": "275",
            "name": "Avdat",
            "lat": "30.7927",
            "lon": "34.7749",
            "zoom": "1",
            "height": "600",
            "is_park": "1"
        },
        "277": {
            "lid": "277",
            "name": "Hay-Bar Yotvata",
            "lat": "29.8691",
            "lon": "35.0430",
            "zoom": "1",
            "height": "65",
            "is_park": "1"
        },
        "278": {
            "lid": "278",
            "name": "Coral Beach",
            "lat": "29.5082",
            "lon": "34.9214",
            "zoom": "4",
            "height": "0",
            "is_park": "1"
        }
    }

        lid = str(lid)
        if self.language=="he":
            location_map = HE_LOCATIONS
        else:
            location_map = EN_LOCATIONS
        return location_map.get(lid, "Nothing")["name"]

    def get_weather_description_by_code(self,weather_code):
        
        '''
        Converts the weather code to name
        '''
        
        HE_WEATHER_CODES = {
                "1250": "בהיר",
                "1220": "מעונן חלקית",
                "1230": "מעונן",
                "1570": "אביך",
                "1010": "סופות חול",
                "1160": "ערפל",
                "1310": "חם",
                "1580": "חם מאד",
                "1270": "הביל",
                "1320": "קר",
                "1590": "קר מאד",
                "1300": "קרה",
                "1530": "מעונן חלקית, יתכן גשם",
                "1540": "מעונן, יתכן גשם",
                "1560": "מעונן עם גשם קל",
                "1140": "גשום",
                "1020": "סופות רעמים",
                "1510": "סוער",
                "1260": "רוחות חזקות",
                "1080": "שלג מעורב בגשם",
                "1070": "שלג קל",
                "1060": "שלג",
                "1520": "שלג כבד",
            }

        EN_WEATHER_CODES = {
                "1250": "Clear",
                "1220": "Partly cloudy",
                "1230": "Cloudy",
                "1570": "Dust",
                "1010": "Sandstorms",
                "1160": "Fog",
                "1310": "Hot",
                "1580": "Extremely hot",
                "1270": "Muggy",
                "1320": "Cold",
                "1590": "Extremely  cold",
                "1300": "Frost",
                "1530": "Partly cloudy, possible rain",
                "1540": "Cloudy, possible rain",
                "1560": "Cloudy, light rain",
                "1140": "Rainy",
                "1020": "Thunderstorms",
                "1510": "Stormy",
                "1260": "Windy",
                "1080": "Sleet",
                "1070": "Light snow",
                "1060": "Snow",
                "1520": "Heavy snow",
            }

        if self.language == "he":
            description_map = HE_WEATHER_CODES
        else:
            description_map = EN_WEATHER_CODES
        return description_map.get(str(weather_code), "Nothing")

    def get_wind_direction(self,direction_code):
        '''
        Converts the wind direction code to name
        '''
        HE_WIND_DIRECTIONS = {
        "360": "צפון",
        "23": "North North East",
        "45": "צפון מזרח",
        "68": "צפון מזרח-מזרח",
        "90": "מזרח",
        "113": "East South East",
        "135": "דרום מזרח",
        "158": "South South East",
        "180": "דרום",
        "203": "South South West",
        "225": "דרום מערב",
        "248": "West South West",
        "270": "מערב",
        "293": "צפון מערב-מערב",
        "315": "צפון מערב",
        "338": "צפון-צפון מערב",
        "0": "צפון"
    }

        EN_WIND_DIRECTIONS = {
        "360": "North",
        "23": "North North East",
        "45": "North East",
        "68": "East North East",
        "90": "East",
        "113": "East South East",
        "135": "South East",
        "158": "South South East",
        "180": "South",
        "203": "South South West",
        "225": "South West",
        "248": "West South West",
        "270": "West",
        "293": "West North West",
        "315": "North West",
        "338": "North North West",
        "0": "North"
    }

        WIND_DIRECTIONS_IDS = {"1":"360",
                                    "2":"23",
                                    "3":"45",
                                    "4":"68",
                                    "5":"90",
                                    "6":"113",
                                    "7":"135",
                                    "8":"158",
                                    "9":"180",
                                    "10":"203",
                                    "11":"225",
                                    "12":"248",
                                    "13":"270",
                                    "14":"293",
                                    "15":"315",
                                    "16":"338",
                                    "17":"0"}

        wind_direction = WIND_DIRECTIONS_IDS.get(direction_code, "Nothing")
        if self.language == "he":
            description_map = HE_WIND_DIRECTIONS
        else:
            description_map = EN_WIND_DIRECTIONS
        return description_map.get(str(wind_direction), "Nothing")

    def get_day_of_the_week(self,date):
        
        '''
        Converts the given date to day of the week name
        '''
        weekday = {
            "Sunday":"ראשון",
            "Monday":"שני",
            "Tuesday":"שלישי",
            "Wednesday":"רביעי",
            "Thursday":"חמישי",
            "Friday":"שישי",
            "Saturday":"שבת",
        }
        day = pd.Timestamp(date).day_name()
        if self.language=="he":
            return weekday.get(day, "nothing")
        else:
            return day