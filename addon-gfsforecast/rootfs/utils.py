import math
from mapping import *

def get_wind_info(vwind: float, uwind: float, metric_system: bool) -> tuple[float, int]:
    windangle = int((270 - math.atan2(vwind, uwind) * 180 / math.pi) % 360)
    windspeed = math.sqrt(vwind * vwind + uwind * uwind)
    if not metric_system:
        windspeed = convert_ms_to_mph(windspeed)
    windspeed = round(windspeed, 1)
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

def get_condition(chance_of_sun: int, rain: float, temperature_min: float) -> str:
    if rain > 0.2:
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
        if chance_of_sun <= 10:
            return 'cloudy'
        elif  chance_of_sun <= 80:
            return 'partlycloudy'
    return 'sunny'

def convert_celcius_to_fahrenheit(value_c: float) -> float:
    return round(value_c * 1.8 + 32, 1)

def convert_mm_to_inch(value: float) -> float:
    return value / 25.4

def convert_hPa_to_inchHg(value: float) -> float:
    return value * 0.0295

def convert_ms_to_mph(value: float) -> float:
    return value * 2.23694