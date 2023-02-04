#Helpers Methods
import config
import requests
import datetime

def getWeatherInfo(fecha, proyecto):
    #get wind speed and direction from openweather api

    url = config.OW_URL + "lat=" + str(proyecto["Latitud"]) + "&lon=" + str(proyecto["Longitud"]) + "&appid=" + config.OW_APIKEY
    response = requests.get(url)
    data = response.json()
    result = {}
    for i in range(len(data["list"])):
        utc_time=datetime.datetime.fromtimestamp(data["list"][i]["dt"])
        chile_time=(utc_time+datetime.timedelta(hours=config.CHILETIMEZONE)).strftime("%d-%m-%Y %H:%M:%S")
        wind_speed = data["list"][i]["wind"]["speed"]
        wind_direction = data["list"][i]["wind"]["deg"]
        result.update({chile_time: {"wind_speed": wind_speed, "wind_direction": wind_direction}})
        
    """pretty_json = json.dumps(result, indent=4)
    with open("result.json", "w") as f:
        f.write(pretty_json)"""
    return result


"""proyecto = {"Latitud": -33.4569, "Longitud": -70.6483}
fecha = "2020-05-01"
getWeatherInfo(fecha, proyecto)"""


