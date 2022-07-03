from cmath import log
import json
import os
import paho.mqtt.client as mqtt 
import logging
import time
import sys
import getopt
from typing import Any
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    fmt='[%(asctime)s] %(levelname)s: %(log_color)s%(message)s%(reset)s', 
    datefmt='%H:%M:%S',
    log_colors={
		'DEBUG':    'black',
		'INFO':     'green',
		'WARNING':  'yellow',
		'ERROR':    'red',
		'CRITICAL': 'red,bg_white',
	}))
logger = colorlog.getLogger()
logger.addHandler(handler)

log_levels = {
    'trace': logging.DEBUG,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'notice': logging.WARNING,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'fatal': logging.FATAL
}

device = ""
broker = ""
port = 1883
mqtt_user = ""
mqtt_pass = ""
discovery_prefix = "homeassistant"
unit_system = "Metric"
interval = 5
new_sensor_used = False
log_level = "info"

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:b:P:u:p:I:s:i:nl:",["device=","broker=","port=","user=","password=","prefix=","system=","interval=","new_sensor", "log_level="])
except getopt.GetoptError:
    print('vproweather2mqtt.py -d <device> -b <broker>[-P <port>][-u <user>][-p <password>][-I <prefix>][-s <system>][-i <interval][-l <loglevel>][-n]')
    sys.exit(2)
for opt, arg in opts:
    if opt in ('-d',"--device"):
        device = arg
    elif opt in ("-b", "--broker"):
        broker = arg
    elif opt in ("-P", "--port"):
        port = int(arg)
    elif opt in ("-u", "--user"):
        mqtt_user = arg
    elif opt in ("-p", "--password"):
        mqtt_pass = arg
    elif opt in ("-I", "--prefix"):
        discovery_prefix = arg
    elif opt in ("-s", "--system"):
        unit_system = arg
    elif opt in ("-i", "--interval"):
        interval = int(arg)
    elif opt in ("-n", "--new_sensor"):
        new_sensor_used = True
    elif opt in ("-l", "--log_level"):
        log_level = arg

logger.setLevel(log_levels[log_level])

logger.debug(f"device = {device}")
logger.debug(f"broker = {broker}")
logger.debug(f"port = {port}")
logger.debug(f"mqtt_user = {mqtt_user}")
logger.debug(f"mqtt_pass = {mqtt_pass}")
logger.debug(f"discovery_prefix = {discovery_prefix}")
logger.debug(f"unit_system = {unit_system}")
logger.debug(f"interval = {interval}")
logger.debug(f"log_level = {log_level}")
logger.debug(f"new_sensor_used = {new_sensor_used}")

if not device:
    logger.error("Must define DEVICE in configuration!")
    exit(1)

if not broker:
    logger.error("Must define MQTT Broker in configuration!")
    exit(1)

metric_system = unit_system == 'Metric'

long_names = {
#    "15mRain": "Rain (15 Minute)",
    "BaroCurr": "Barometric Pressure",
    "BaroTrend": "Barometric Trend",
    "BaroTrendImg": "Barometric Trend Image",
    "BattVoltage": "Battery Voltage",
    "DavisTime": "Davis Time",
    "DayET": "Evapotranspiration Total (Day)",
    "DayRain": "Rain (Day)",
    "ExtraTemp1": "Extra Temperature 1",
    "ExtraTemp2": "Extra Temperature 2",
    "ExtraTemp3": "Extra Temperature 3",
    "ExtraTemp4": "Extra Temperature 4",
    "ExtraTemp5": "Extra Temperature 5",
    "ExtraTemp6": "Extra Temperature 6",
    "ExtraTemp7": "Extra Temperature 7",
    "FeelsLike": "Feels Like",
    "ForeIcon": "Forecast Icon",
    "ForeRule": "Forecast Rule",
    "Forecast": "Forecast",
    "HeatIndex": "Heat Index",
#    "HourRain": "Rain (Hour)",
    "InsideHum": "Humidity (Inside)",
    "InsideTemp": "Temperature (Inside)",
    "IsRaining": "Is Raining",
    "LeafTemp1": "Leaf Temperature 1",
    "LeafTemp2": "Leaf Temperature 2",
    "LeafTemp3": "Leaf Temperature 3",
    "LeafTemp4": "Leaf Temperature 4",
    "MonthET": "Evapotranspiration Total (Month)",
    "MonthRain": "Rain (Month)",
    "OutsideHum": "Humidity",
    "OutsideTemp": "Temperature",
    "RainRate": "Rain Rate",
    "RainStorm": "Rain Storm",
    "SoilTemp1": "Soil Temperature 1",
    "SoilTemp2": "Soil Temperature 2",
    "SoilTemp3": "Soil Temperature 3",
    "SoilTemp4": "Soil Temperature 4",
    "SolarRad": "Solar Radiation",
    "StormStartDate": "Storm Start Date",
#    "ThswIndex": "THSW Index",
    "UVLevel": "UV Level",
    "Wind10mGustMaxDir": "Wind 10 minute Gust Max. Direction",
    "Wind10mGustMaxDirRose": "Wind 10 minute Gust Max. Direction Rose",
    "Wind10mGustMaxSpeed": "Wind 10 minute Gust Max. Speed",
    "Wind2mAvgSpeed": "Wind 2 minute Average Speed",
    "WindAvgSpeed": "Wind 10 minute Average Speed",
    "WindChill": "Wind Chill",
    "WindDir": "Wind Direction",
    "WindDirRose": "Wind Direction Rose",
    "WindSpeed": "Wind Speed",
    "WindSpeedBft": "Wind Speed (Bft)",
#    "XmitBattt": "Transmit Battery Status",
    "YearRain": "Rain (Year)",
    "YearET": "Evapotranspiration Total (Year)"
}

json_data = {}
prefix = 'vproweather'
vproweather_path = '/vproweather/vproweather'
hass_configured = False

def convert_to_celcius(value: float) -> float:
    return round((value - 32.0) * (5.0/9.0), 1) if metric_system else value
    
def convert_to_kmh(value: float) -> float:
    return round(value * 1.609344, 1) if metric_system else value

def convert_to_mbar(value: float) -> float:
    return round(value * 33.8637526, 1) if metric_system else value

def convert_to_mm(value: float) -> float:
    return round(value * 20.0, 1) if metric_system else value # Use metric tipping bucket modification

def convert_clicks_to_mm(value: int) -> float:
    return round(value * 0.20, 1) if metric_system else value * 0.01 # Use metric tipping bucket modification

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

def get_long_name(name: str) -> str:
    if name in long_names:
        return long_names[name]
    else:
        return name

def calc_heat_index(temperature_f: float, humidity: float, metric_system: bool = True) -> float:
    if temperature_f < 80.0 or humidity < 40.0:
        return convert_to_celcius(temperature_f) if metric_system else temperature_f
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

    return convert_to_celcius(heat_index_f) if metric_system else heat_index_f

def calc_wind_chill(temperature_f: float, windspeed: float, metric_system: bool = True) -> float:
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

    if metric_system:
        return convert_to_celcius(wind_chill_f)
    else:
        return wind_chill_f

def calc_feels_like(windchill_f: float, heatindex_f: float, temperature_f: float, metric_system: bool = True) -> float:
    if temperature_f <= 61:
        feels_like_f = windchill_f
    elif temperature_f >= 70:
        feels_like_f = heatindex_f
    else:
        feels_like_f = temperature_f 
    if metric_system:
        return convert_to_celcius(feels_like_f)
    else:
        return feels_like_f

def convert_raw_data_to_json(raw_data: str) -> dict:
    data_lines = raw_data.split('\n')
    json_data = {}
    for line in data_lines:
        try:
            key,value = line.split(' = ', 1)
            key = key.lstrip('rt')
            if not key in long_names:
                continue
            value = value.strip()
            try:
                fvalue = float(value)
                if key in ['InsideTemp', 'OutsideTemp', 'ThswIndex'] \
                    or key.startswith('ExtraTemp') \
                    or key.startswith('SoilTemp') \
                    or key.startswith('LeafTemp'):
                    if key in ['OutsideTemp'] and new_sensor_used:
                        fvalue -= 0.9
                    json_data[key] = { 
                        'value': convert_to_celcius(fvalue),
                        'value_F': fvalue,
                        'unit_of_measure': '°C' if metric_system else '°F', 
                        'device_class': 'temperature'
                    }
                elif key in ['BaroCurr']:
                    json_data[key] = { 
                        'value': convert_to_mbar(fvalue), 
                        'unit_of_measure': 'hPa' if metric_system else "inHg", 
                        'device_class': 'pressure'
                    }
                elif key in ['RainStorm', 'DayRain', 'MonthRain', 'YearRain', 'DayET', 'MonthET', 'YearET', '15mRain', 'HourRain']:
                    json_data[key] = { 
                        'value': convert_to_mm(fvalue), 
                        'unit_of_measure': 'mm' if metric_system else "inch",
                        'icon': 'mdi:water'
                    }
                elif key in ['RainRate']:
                    json_data[key] = { 
                        'value': convert_clicks_to_mm(fvalue), 
                        'unit_of_measure': 'mm/h' if metric_system else "inch/h",
                        'icon': 'mdi:water'
                    }
                elif key in ['WindSpeed', 'WindAvgSpeed', 'Wind2mAvgSpeed', 'Wind10mGustMaxSpeed']:
                    json_data[key] = {
                        'value': convert_to_kmh(fvalue), 
                        'value_mph': fvalue,
                        'unit_of_measure': 'km/h' if metric_system else "mph",
                        'icon': 'mdi:weather-windy'
                    }
                elif key in ['InsideHum', 'OutsideHum'] or key.startswith('ExtraHum'):
                    json_data[key] = { 
                        'value': fvalue, 
                        'unit_of_measure': '%', 
                        'device_class': 'humidity'
                    }
                elif key in ['BattVoltage']:
                    json_data[key] = { 
                        'value': fvalue, 
                        'unit_of_measure': 'V',
                        'device_class': 'voltage'
                    }
                elif key in ['WindDir', 'Wind10mGustMaxDir']:
                    json_data[key] = {
                        'value': fvalue,
                        'unit_of_measure': '°'
                    }
                else:
                    json_data[key] = { 
                        'value': fvalue
                    }

            except:
                if key in ['IsRaining']:
                    json_data[key] = {
                        'value': 'ON' if value == 'yes' else 'OFF',
                        'component': 'binary_sensor'
                    }
                else:
                    json_data[key] = { 
                        'value': value
                    }
        except ValueError as e:
            pass

    # Overwrite HeatIndex and WindChill read from Davis
    if 'OutsideTemp' in json_data:
        if 'OutsideHum' in json_data:
            heat_index_F = calc_heat_index(json_data['OutsideTemp']['value_F'], json_data['OutsideHum']['value'], False)
            json_data['HeatIndex'] = { 
                'value': convert_to_celcius(heat_index_F),
                'value_F': heat_index_F,
                'unit_of_measure': '°C' if metric_system else '°F', 
                'device_class': 'temperature'
            }

        if 'WindSpeed' in json_data:
            wind_chill_F =  calc_wind_chill(json_data['OutsideTemp']['value_F'], json_data['WindSpeed']['value'], False)
            json_data['WindChill'] = {
                'value': convert_to_celcius(wind_chill_F),
                'value_F': wind_chill_F,
                'unit_of_measure': '°C' if metric_system else '°F', 
                'device_class': 'temperature'
            }

        if 'WindChill' in json_data and 'HeatIndex' in json_data:
            json_data['FeelsLike'] = {
                'value': calc_feels_like(json_data['WindChill']['value_F'], json_data['HeatIndex']['value_F'], json_data['OutsideTemp']['value_F']),
                'unit_of_measure': '°C' if metric_system else '°F', 
                'device_class': 'temperature'
            }

    if metric_system and 'WindAvgSpeed' in json_data:
        json_data['WindSpeedBft'] = { 
            'value': convert_kmh_to_bft(json_data['WindAvgSpeed']['value']),
            'unit_of_measure': 'Bft'
        }
    return json_data

def send_config_to_mqtt(client: Any, json_data: dict, model: str) -> None:
    for key, raw_value in json_data.items():
        device_class = '' 
        unit_of_measure = ''
        component = 'sensor'
        icon = ''
        if 'unit_of_measure' in raw_value:
            unit_of_measure = raw_value['unit_of_measure']
        if 'device_class' in raw_value:
            device_class = raw_value['device_class']
        if 'icon' in raw_value:
            icon = raw_value['icon']
        if 'component' in raw_value:
            component = raw_value['component']
        config_payload = {}
        config_payload["~"] = f"{discovery_prefix}/{component}/{prefix}/{key}"
        config_payload["name"] = get_long_name(key) 
        config_payload["stat_t"] = "~/state"
        config_payload["uniq_id"] = f"sensor.{prefix}_{key.lower()}"
        config_payload['dev'] = { 
            "ids": [prefix], 
            "name": prefix, 
            "mf": "Davis" , 
            "mdl": model
        }
        if unit_of_measure:
            config_payload["unit_of_meas"] = unit_of_measure
        if device_class:
            config_payload["dev_cla"] = device_class
        if icon:
            config_payload['ic'] = icon
        client.publish(f"{config_payload['~']}/config", json.dumps(config_payload), retain=True)
        logger.debug(f"Sent config for sensor {config_payload['~']}")

def send_data_to_mqtt(client: Any, json_data: dict):
    for key, raw_value in json_data.items():
        component = 'sensor'
        value = raw_value['value']
        if 'component' in raw_value:
            component = raw_value['component']
        client.publish(f"{discovery_prefix}/{component}/{prefix}/{key}/state", value, retain=True)

def get_davis_model() -> str:
    proces = f"{vproweather_path} -m {device} 2>/dev/null"
    output = os.popen(proces)
    model = output.read()
    output.close()
    if model == '':
        logger.error('Couldn''t determine model')
        exit(2)
    return model.lstrip('Model: ').strip('\n')

def set_davis_time() -> None:
    proces = f"{vproweather_path} -s {device} 2>/dev/null"
    output = os.popen(proces)
    output.close()
    logger.info('Set weather station time to system time')

#
# MAIN
#
client = mqtt.Client()

if mqtt_user and mqtt_pass:
    logger.debug('Added MQTT user and password')
    client.username_pw_set(mqtt_user, mqtt_pass)

try:
    client.connect(broker, port)
except:
   logger.error("Connection to MQTT failed. Make sure broker, port, and user is defined correctly")
   exit(1)

model = get_davis_model()
logger.info("Found model: " + model)

if not hass_configured:
    set_davis_time()

while True:
    ready_to_send = True
    logger.info(f"Acquiring data from {device} using vproweather")
    process = f"{vproweather_path} -x -t -d 15 {device} 2>/dev/null"
    logger.debug('Executing ' + process)
    output = os.popen(process)
    data = output.read()
    output.close()
    if data == '':
        logger.error('Error acquiring data')
        ready_to_send = False
        # client.disconnect()
        # exit(2)

    json_data = convert_raw_data_to_json(data)

    if not contains_correct_data(json_data):
        logger.error(f"Incorrect data found: {json.dumps(json_data)}")
        ready_to_send = False

    if ready_to_send:
        if not hass_configured:
            logger.info('Initializing sensors from Home Assistant to auto discover.')
            send_config_to_mqtt(client, json_data, model)
            hass_configured = True

        send_data_to_mqtt(client, json_data)
        logger.info('Data sent to MQTT')

    time.sleep(interval)
