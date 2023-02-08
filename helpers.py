"""Helpers Methods"""
import datetime
import requests
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


#x = {"Latitud": -33.4569, "Longitud": -70.6483}
#r = get_weather_info(x)
