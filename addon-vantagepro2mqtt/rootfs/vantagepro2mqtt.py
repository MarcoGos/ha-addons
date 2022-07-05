import sys, getopt
import json
import logging
import colorlog
import time
import paho.mqtt.client as mqtt 
from pyvantagepro import VantagePro2
from utils import *
from mapping import (MAPPING)
from typing import Any

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
prefix = 'vantagepro'
unit_system = "Metric"
hass_configured = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:b:P:u:p:I:s:i:nl:",["device=","broker=","port=","user=","password=","prefix=","system=","interval=","new_sensor", "log_level="])
except getopt.GetoptError:
    print('vantagepro2mqtt.py -d <device> -b <broker>[-P <port>][-u <user>][-p <password>][-I <prefix>][-s <system>][-i <interval][-l <loglevel>][-n]')
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

metric_system = unit_system == 'Metric'
# discovery_prefix = "homeassistant"

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

def send_config_to_mqtt(client: Any, data: Any) -> None:
    for key, value in data.items():
        if not key in MAPPING:
            continue
        if 'has_correct_value' in MAPPING[key]:
            if not MAPPING[key]['has_correct_value'](value):
                continue
        device_class = '' 
        unit_of_measure = ''
        component = 'sensor'
        icon = ''
        if 'unit_of_measure' in MAPPING[key]:
            unit_of_measure =  MAPPING[key]['unit_of_measure']
            if type(unit_of_measure) is dict:
                unit_of_measure = unit_of_measure['metric' if metric_system else 'imperial']
        if 'device_class' in MAPPING[key]:
            device_class = MAPPING[key]['device_class']
        if 'icon' in MAPPING[key]:
            icon = MAPPING[key]['icon']
        if 'component' in MAPPING[key]:
            component = MAPPING[key]['component']
        config_payload = {}
        config_payload["~"] = f"{discovery_prefix}/{component}/{prefix}/{MAPPING[key]['topic']}"
        config_payload["name"] = MAPPING[key]['long_name'] 
        config_payload["uniq_id"] = f"{prefix}_{MAPPING[key]['topic'].lower()}"
        config_payload["stat_t"] = "~/state"
        config_payload['dev'] = { 
            "ids": [prefix], 
            "name": prefix, 
            "mf": "Davis"
        }
        if unit_of_measure:
            config_payload["unit_of_meas"] = unit_of_measure
        if device_class:
            config_payload["dev_cla"] = device_class
        if icon:
            config_payload['ic'] = icon
        client.publish(f"{config_payload['~']}/config", json.dumps(config_payload), retain=True)
        logger.debug(f"Sent config for sensor {config_payload['~']}")

def send_data_to_mqtt(client: Any, data: dict):
    for key, value in data.items():
        if not key in MAPPING:
            continue
        if 'has_correct_value' in MAPPING[key]:
            if not MAPPING[key]['has_correct_value'](value):
                continue

        if 'component' in MAPPING[key]:
            component = MAPPING[key]['component']
        else:
            component = 'sensor'
        if 'correction' in MAPPING[key]:
            value = MAPPING[key]['correction'](value)
        if metric_system and 'conversion' in MAPPING[key]:
            value = MAPPING[key]['conversion'](value)
        logger.debug(f"{key}={value} (type={type(value)})")
        client.publish(f"{discovery_prefix}/{component}/{prefix}/{MAPPING[key]['topic']}/state", value, retain=True)

def add_additional_info(data: dict):
    data['HeatIndex'] = calc_heat_index(data['TempOut'], data['HumOut'])
    data['WindChill'] = calc_wind_chill(data['TempOut'], data['WindSpeed'])
    data['FeelsLike'] = calc_feels_like(data['TempOut'], data['HumOut'], data['WindSpeed'])
    data['WindDirRose'] = get_wind_rose(data['WindDir'])
    if metric_system:
        data['WindSpeedBft'] = convert_kmh_to_bft(convert_to_kmh(data['WindSpeed10Min']))
    data['IsRaining'] = "ON" if data['RainRate'] > 0 else "OFF"

def correct_temperature(data: dict):
    if 'TempOut' in data:
        data['TempOut'] -= 0.9
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

logger.info(f"Acquiring data from {device} using vproweather")
try:
    device = VantagePro2.from_url(f'serial:{device}:19200:8N1')
except Exception as e:
    logger.error(f'{e}')
    exit(1)

if not hass_configured:
    logger.info('Set weather station time to system time')
    device.settime(datetime.now())

while True:
    data = device.get_current_data()
    if new_sensor_used:
        correct_temperature(data)
    add_additional_info(data)

    if not hass_configured:
        logger.info('Initializing sensors from Home Assistant to auto discover.')
        send_config_to_mqtt(client, data)
        hass_configured = True

    send_data_to_mqtt(client, data)
    logger.info('Data sent to MQTT')

    time.sleep(interval)
