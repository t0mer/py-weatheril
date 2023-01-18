"""Israel Meteorological Service unofficial python api wrapper"""
import os
import json
import requests
import pandas as pd
from PIL import Image
from .forcast import *
from .weather import *
from loguru import logger
from urllib.parse import urlparse
from .radarsatellite import RadarSatellite



locations_url = "https://ims.gov.il/{}/locations_info"
forcast_url = "https://ims.gov.il/{}/forecast_data/{}"
radar_url = "https://ims.gov.il/{}/radar_satellite"
current_analysis_url = "https://ims.gov.il/{}/now_analysis"
weather_codes_url = "https://ims.gov.il/{}/weather_codes"


class WeatherIL:

    def __init__(self, location,language="he"):
        """
        Init the WeatherIL object.
        parameters:
            >>> location: Location Id for the forcast (Table exists in the readme)
            >>> language: can be he (Hebrew) or en (English). default will be he
        """
        self.language = language
        self.location = location
    
    def get_current_analysis(self):
        try:
            data = self.get_data(current_analysis_url.format(self.language))
            weather_data = data["data"][self.location]
            weather = Weather(lid=weather_data["lid"],
                                location=self.get_location_name_by_id(weather_data["lid"]),
                                humidity=weather_data["relative_humidity"],
                                rain=weather_data["rain"],
                                temperature=weather_data["temperature"],
                                wind_speed=weather_data["wind_speed"],
                                feels_like=weather_data["feels_like"],
                                json = weather_data)
            return weather
        except Exception as e:
            logger.error("Error getting current analysis " + e)
            return None
 
    def get_forcast(self):
        '''
        Get weather forcast
        return: Forcast object
        '''
        try:
            data = self.get_data(forcast_url.format(self.language,self.location))
            forcast = Forcast()
            for key in data["data"].keys():
                    day = self.get_day_of_the_week(key)
                    hours = self.get_hourly_forcast(data["data"][key]["hourly"])
                    if "description" in str(data):
                        try:
                            description = data["data"][key]["country"]["description"]
                        except:
                            description = ""
                    else:
                        description = ""
                    daily = Daily(
                        date = key,
                        location = self.get_location_name_by_id(data["data"][key]["daily"]["lid"]),
                        day = day,
                        weather=self.get_weather_name_by_code(data["data"][key]["daily"]["weather_code"]),
                        minimum_temperature=data["data"][key]["daily"]["minimum_temperature"],
                        maximum_temperature=data["data"][key]["daily"]["maximum_temperature"],
                        maximum_uvi=data["data"][key]["daily"]["maximum_uvi"],
                        hours=hours,
                        description=description
                        
                    )
                    forcast.days.append(daily)
                    
            return forcast
        except Exception as e:
            logger.error("Error getting forcast data " + e)
            return None   
       
    def get_hourly_forcast(self,data):
        '''
        Get the hourly forcast
        '''
        hours = []
        try:
            for key in data.keys():
                hours.append(
                    Hourly(key,self.get_weather_name_by_code(data[key]["weather_code"]),int(data[key]["temperature"]))
                )
            return hours
        except Exception as e:
            logger.error("Error getting hourly forcast" + e)
            return None


    def get_radar_images(self):
        '''
        Get the list of images for Satellite and Radar
        return: RadarSatellite objects with the lists
        '''
        images_url = "https://ims.gov.il"
        rs = RadarSatellite()
        try:
            data = self.get_data(radar_url.format(self.language))
            for key in data["data"]["types"]["IMSRadar"]:
                rs.imsradar_images.append(images_url + key["file_name"])

            for key in data["data"]["types"]["radar"]:
                rs.radar_images.append(images_url + key["file_name"])

            for key in data["data"]["types"]["MIDDLE-EAST"]:
                rs.middle_east_satellite_images.append(images_url + key["file_name"])

            for key in data["data"]["types"]["EUROPE"]:
                rs.europe_satellite_images.append(images_url + key["file_name"])
            return rs
        except Exception as e:
            logger.error("Error getting images. " + e)
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
            logger.error("Error getting data. " + str(e))
            return ""


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

    def get_weather_name_by_code(self,weather_code):
        '''
        Converts the weather code to name
        '''
        if self.language == "he":
            weather = {
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
        else:
             weather = {
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
        return weather.get(str(weather_code), "nothing")

    def get_location_name_by_id(self,lid):
        '''
        Converts location id to City name
        '''
        lid = str(lid)
        if self.language=="he":
            location = {
                "1":"ירושלים",
                "2":"תל אביב-יפו",
                "3":"חיפה",
                "4":"ראשון לציון",
                "5":"פתח תקווה",
                "6":"אשדוד",
                "7":"נתניה",
                "8":"באר שבע",
                "9":"בני ברק",
                "10":"חולון",
                "11":"רמת גן",
                "12":"אשקלון",
                "13":"רחובות",
                "14":"בת ים",
                "15":"בית שמש",
                "16":"כפר סבא",
                "17":"הרצליה",
                "18":"חדרה",
                "19":"מודיעין",
                "20":"רמלה",
                "21":"רעננה",
                "22":"מודיעין עילית",
                "23":"רהט",
                "24":"הוד השרון",
                "25":"גבעתיים",
                "26":"קריית אתא",
                "27":"נהריה",
                "28":"ביתר עילית",
                "29":"אום אל-פחם",
                "30":"קריית גת",
                "31":"אילת",
                "32":"ראש העין",
                "33":"עפולה",
                "34":"נס ציונה",
                "35":"עכו",
                "36":"אלעד",
                "37":"רמת השרון",
                "38":"כרמיאל",
                "39":"יבנה",
                "40":"טבריה",
                "41":"טייבה",
                "42":"קריית מוצקין",
                "43":"שפרעם",
                "44":"נוף הגליל",
                "45":"קריית ים",
                "46":"קריית ביאליק",
                "47":"קריית אונו",
                "48":"מעלה אדומים",
                "49":"אור יהודה",
                "50":"צפת",
                "51":"נתיבות",
                "52":"דימונה",
                "53":"טמרה",
                "54":"סח'נין",
                "55":"יהוד",
                "56":"באקה אל גרבייה",
                "57":"אופקים",
                "58":"גבעת שמואל",
                "59":"טירה",
                "60":"ערד",
                "61":"מגדל העמק",
                "62":"שדרות",
                "63":"עראבה",
                "64":"נשר",
                "65":"קריית שמונה",
                "66":"יקנעם עילית",
                "67":"כפר קאסם",
                "68":"כפר יונה",
                "69":"קלנסווה",
                "70":"קריית מלאכי",
                "71":"מעלות-תרשיחא",
                "72":"טירת כרמל",
                "73":"אריאל",
                "74":"אור עקיבא",
                "75":"בית שאן",
                "76":"מצפה רמון",
                "77":"לוד",
                "78":"נצרת",
                "79":"קצרין",
                "80":"עין גדי",
             }
        else:
            location = {
                "1":"Jerusalem",
                "2":"Tel Aviv - Yafo",
                "3":"Haifa",
                "4":"Rishon le Zion",
                "5":"Petah Tiqva",
                "6":"Ashdod",
                "7":"Netania",
                "8":"Beer Sheva",
                "9":"Bnei Brak",
                "10":"Holon",
                "11":"Ramat Gan",
                "12":"Asheqelon",
                "13":"Rehovot",
                "14":"Bat Yam",
                "15":"Bet Shemesh",
                "16":"Kfar Sava",
                "17":"Herzliya",
                "18":"Hadera",
                "19":"Modiin",
                "20":"Ramla",
                "21":"Raanana",
                "22":"Modiin Illit",
                "23":"Rahat",
                "24":"Hod Hasharon",
                "25":"Givatayim",
                "26":"Kiryat Ata",
                "27":"Nahariya",
                "28":"Beitar Illit",
                "29":"Um al-Fahm",
                "30":"Kiryat Gat",
                "31":"Eilat",
                "32":"Rosh Haayin",
                "33":"Afula",
                "34":"Nes-Ziona",
                "35":"Akko",
                "36":"Elad",
                "37":"Ramat Hasharon",
                "38":"Karmiel",
                "39":"Yavneh",
                "40":"Tiberias",
                "41":"Tayibe",
                "42":"Kiryat Motzkin",
                "43":"Shfaram",
                "44":"Nof Hagalil",
                "45":"Kiryat Yam",
                "46":"Kiryat Bialik",
                "47":"Kiryat Ono",
                "48":"Maale Adumim",
                "49":"Or Yehuda",
                "50":"Zefat",
                "51":"Netivot",
                "52":"Dimona",
                "53":"Tamra ",
                "54":"Sakhnin",
                "55":"Yehud",
                "56":"Baka al-Gharbiya",
                "57":"Ofakim",
                "58":"Givat Shmuel",
                "59":"Tira",
                "60":"Arad",
                "61":"Migdal Haemek",
                "62":"Sderot",
                "63":"Araba",
                "64":"Nesher",
                "65":"Kiryat Shmona",
                "66":"Yokneam Illit",
                "67":"Kafr Qassem",
                "68":"Kfar Yona",
                "69":"Qalansawa",
                "70":"Kiryat Malachi",
                "71":"Maalot-Tarshiha",
                "72":"Tirat Carmel",
                "73":"Ariel",
                "74":"Or Akiva",
                "75":"Bet Shean",
                "76":"Mizpe Ramon",
                "77":"Lod",
                "78":"Nazareth",
                "79":"Qazrin",
                "80":"En Gedi",
            }
        return location.get(lid, "nothing")