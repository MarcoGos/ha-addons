from datetime import datetime
from time import strftime

def convert_to_celcius(value: float) -> float:
    return round((value - 32.0) * (5.0/9.0), 1)
    
def convert_to_kmh(value: float) -> float:
    return round(value * 1.609344, 1)

def convert_to_mbar(value: float) -> float:
    return round(value * 33.8637526, 1)

def convert_to_mm(value: float) -> float:
    return round(value * 20.0, 1) # Use metric tipping bucket modification

def convert_kmh_to_ms(windspeed: float) -> float:
    return round(windspeed / 3.6, 1)

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

def convert_kmh_to_bft(windspeed_kmh: float) -> int:
    return convert_ms_to_bft(convert_kmh_to_ms(windspeed_kmh))

def contains_correct_data(json_data: dict):
    return json_data['OutsideTemp']['value'] < 60 \
        and json_data['RainRate']['value'] < 1000 \
        and json_data['WindSpeed']['value'] < 40 \
        and json_data['OutsideHum']['value'] < 100 \
        and json_data['WindAvgSpeed']['value'] < 250

def calc_heat_index(temperature_f: float, humidity: float) -> float:
    if temperature_f < 80.0 or humidity < 40.0:
        return temperature_f
    else:
        heat_index_f = \
            -42.379 \
            + (2.04901523 * temperature_f) \
            + (10.14333127 * humidity) \
            - (0.22475541 * temperature_f * humidity) \
            - (0.00683783 * pow(temperature_f, 2)) \
            - (0.05481717 * pow(humidity, 2)) \
            + (0.00122874 * pow(temperature_f, 2) * humidity) \
            + (0.00085282 * temperature_f * pow(humidity, 2)) \
            - (0.00000199 * pow(temperature_f, 2) * pow(humidity, 2))

    if (heat_index_f < temperature_f):
        heat_index_f = temperature_f

    return heat_index_f

def calc_wind_chill(temperature_f: float, windspeed: float) -> float:
    if (windspeed == 0):
        wind_chill_f = temperature_f
    else:
        wind_chill_f = \
            35.74 \
            + (0.6215 * temperature_f) \
            - (35.75 * pow(windspeed,0.16)) \
            + (0.4275 * temperature_f * pow(windspeed, 0.16))
    if (wind_chill_f > temperature_f):
        wind_chill_f = temperature_f

    return wind_chill_f

def calc_feels_like(windchill_f: float, heatindex_f: float, temperature_f: float) -> float:
    if temperature_f <= 61:
        feels_like_f = windchill_f
    elif temperature_f >= 70:
        feels_like_f = heatindex_f
    else:
        feels_like_f = temperature_f 
    return feels_like_f

def convert_to_iso_datetime(value: datetime) -> str:
    return value.strftime('%Y-%m-%dT%H:%M:%S' + strftime('%z'))

def get_wind_rose(bearing: int) -> str:
    if bearing >= 347 and bearing < 12:
        return "N"
    elif bearing >= 12 and bearing < 34:
        return "NNE"
    elif bearing >= 34 and bearing < 57:
        return "NE"
    elif bearing >= 57 and bearing < 79:
        return "ENE"
    elif bearing >= 79 and bearing < 102:
        return "E"
    elif bearing >= 102 and bearing < 124:
        return "ESE"
    elif bearing >= 124 and bearing < 147:
        return "SE"
    elif bearing >= 147 and bearing < 170:
        return "SSE"
    elif bearing >= 170 and bearing < 192:
        return "S"
    elif bearing >= 192 and bearing < 214:
        return "SSW"
    elif bearing >= 214 and bearing < 237:
        return "SW"
    elif bearing >= 237 and bearing < 259:
        return "WSW"
    elif bearing >= 259 and bearing < 280:
        return "W"
    elif bearing >= 280 and bearing < 303:
        return "WNW"
    elif bearing >= 303 and bearing < 347:
        return "NW"
    else:
        return "NNW"

def has_correct_value(value: float) -> bool:
    return value != 255