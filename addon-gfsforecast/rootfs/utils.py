import math
from mapping import *

def get_wind_info(vwind: float, uwind: float) -> tuple[float, int]:
    windangle = int((270 - math.atan2(vwind, uwind) * 180 / math.pi) % 360)
    windspeed = round(math.sqrt(vwind * vwind + uwind * uwind), 1)
    return windspeed, windangle

def convert_ms_to_bft(windspeed: float) -> int:
    if windspeed < 0.2:
        return 0
    elif windspeed < 1.6:
        return 1
    elif windspeed < 3.4:
        return 2
    elif windspeed < 5.5:
        return 3
    elif windspeed < 8.0:
        return 4
    elif windspeed < 10.8:
        return 5
    elif windspeed < 13.9: 
        return 6
    elif windspeed < 17.2:
        return 7
    elif windspeed < 20.8:
        return 8
    elif windspeed < 24.5:
        return 9
    elif windspeed < 28.5:
        return 10
    elif windspeed < 32.7:
        return 11
    else:
        return 12

def get_wind_rose(bearing: int) -> str:
    index = int((bearing/45)+.5)
    directions = ["N","NE","E","SE","S","SW","W","NW"]
    return directions[(index % 8)]

def ms_to_kmh(wind_speed: float) -> float:
    return round(wind_speed * 3.6, 1)

def get_condition(sun_chance: int, rain: float, temperature_min: float) -> str:
    if rain > 0:
        if temperature_min > 3:
            if rain > 2:
                return 'pouring'
            else:
                return 'rainy'
        elif temperature_min >= 0:
            return 'snowy-rainy'
        else:
            return 'snowy'
    else:
        if sun_chance <= 10:
            return 'cloudy'
        elif  sun_chance <= 80:
            return 'partlycloudy'
    return 'sunny'
