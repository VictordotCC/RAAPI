"""Helpers Methods"""
import datetime
import requests

from fastkml import kml

import config


def get_weather_info(proyecto):
    """get wind speed and direction from openweather api"""

    url = (config.OW_URL + "lat=" + str(proyecto["Latitud"]) + "&lon="
        + str(proyecto["Longitud"]) + "&appid=" + config.OW_APIKEY)
    response = requests.get(url, timeout=30)
    data = response.json()
    result = {}
    for i in range(len(data["list"])):
        utc_time=datetime.datetime.fromtimestamp(data["list"][i]["dt"])
        chile_time=((utc_time+datetime.timedelta(hours=config.CHILETIMEZONE))
                    .strftime("%d-%m-%Y %H:%M:%S"))
        wind_speed = data["list"][i]["wind"]["speed"]
        wind_direction = data["list"][i]["wind"]["deg"]
        result.update({chile_time: {"wind_speed": wind_speed, "wind_direction": wind_direction}})
    return result

def leer_kml(kml_file):
    """Read a kml file and return the coordinates"""

    #check if kml_file is a file or a string
    if isinstance(kml_file, str):
        kml_file = kml_file.encode('utf-8')
    else:
        kml_file = kml_file.read()

    with open(kml_file, 'rb') as f:
        doc = f.read()
        k = kml.KML()
        k.from_string(doc)
        k.from_string(doc)
   
        features = list(k.features())
        puntos = []
        for feature in features:
            for group in feature.features():
                for placemark in group.features():
                    puntos.append([placemark.geometry.x, placemark.geometry.y])
    
    return puntos

def get_time():
    """Get the current time"""
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")


#x = {"Latitud": -33.4569, "Longitud": -70.6483}
#r = get_weather_info(x)
