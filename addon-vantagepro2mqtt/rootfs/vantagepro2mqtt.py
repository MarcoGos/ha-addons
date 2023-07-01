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
    datefmt='%Y-%m-%d %H:%M:%S',
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
address = ""
broker = ""
port = 1883
mqtt_user = ""
mqtt_pass = ""
discovery_prefix = "homeassistant"
prefix = 'vantagepro'
unit_system = "Metric"
alt_windspeed_uom = False
hass_configured = False
log_level = 'notice'
interval = 30
new_sensor_used = False
availability_topic = f"{discovery_prefix}/sensor/{prefix}/Status/state"

try:
    opts, args = getopt.getopt(sys.argv[1:], ":d:a:b:P:u:p:I:s:i:nl:k",["device=","address=","broker=","port=","user=","password=","prefix=","system=","interval=","new_sensor", "log_level=", "alt_windspeed_uom"])
except getopt.GetoptError:
    print('vantagepro2mqtt.py [-d <device>|-a <address>] -b <broker>[-P <port>][-u <user>][-p <password>][-I <prefix>][-s <system>][-i <interval][-l <loglevel>][-n][-k]')
    sys.exit(2)
for opt, arg in opts:
    logger.debug(f"{opt}={arg}")
    if opt in ('-d',"--device"):
        if arg != 'null':
            device = arg
    elif opt in ("-a", "--address"):
        if arg != 'null':
            address = arg
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
    elif opt in ("-k", "--alt_windspeed_uom"):
        alt_windspeed_uom = True

metric_system = unit_system == 'Metric'

logger.setLevel(log_levels[log_level])

logger.debug(f"device = {device}")
logger.debug(f"address = {address}")
logger.debug(f"broker = {broker}")
logger.debug(f"port = {port}")
logger.debug(f"mqtt_user = {mqtt_user}")
logger.debug(f"mqtt_pass = {mqtt_pass}")
logger.debug(f"discovery_prefix = {discovery_prefix}")
logger.debug(f"unit_system = {unit_system}")
logger.debug(f"interval = {interval}")
logger.debug(f"log_level = {log_level}")
logger.debug(f"new_sensor_used = {new_sensor_used}")
logger.debug(f"alt_windspeed_uom = {alt_windspeed_uom}")

if not device and not address:
    logger.error("Must define DEVICE or ADDRESS in configuration!")
    exit(1)

if not broker:
    logger.error("Must define MQTT Broker in configuration!")
    exit(1)

def send_config_to_mqtt(client: Any, data: dict[str, Any]) -> None:
    for key in MAPPING.keys():
        if MAPPING[key].get('enable_by_data', False):
            if key in data:
                if 'has_correct_value' in MAPPING[key]:
                    if not MAPPING[key]['has_correct_value'](data[key]):
                        continue
                send_config_entity_to_mqtt(key)
        else:
            send_config_entity_to_mqtt(key)

def send_config_entity_to_mqtt(key: str):
    device_class = '' 
    state_class = ''
    unit_of_measure = ''
    entity_category = ''
    icon = ''
    if 'unit_of_measure' in MAPPING[key]:
        unit_of_measure =  MAPPING[key]['unit_of_measure']
        if type(unit_of_measure) is dict:
            unit_of_measure = unit_of_measure['metric' if metric_system else 'imperial']
        if type(unit_of_measure) is dict:
            if metric_system and alt_windspeed_uom and 'alt' in unit_of_measure:
                unit_of_measure = unit_of_measure['alt']
            else:
                unit_of_measure = unit_of_measure['default']
    device_class = MAPPING[key].get('device_class', '')
    entity_category = MAPPING[key].get('entity_category', '')
    state_class = MAPPING[key].get('state_class', '')
    icon = MAPPING[key].get('icon', '')
    component = MAPPING[key].get('component', 'sensor')
    config_payload = {}
    config_payload["~"] = f"{discovery_prefix}/{component}/{prefix}/{MAPPING[key]['topic']}"
    config_payload["name"] = MAPPING[key]['long_name'] 
    config_payload["uniq_id"] = f"{prefix}_{MAPPING[key]['topic'].lower()}"
    config_payload["stat_t"] = "~/state"
    config_payload['dev'] = { 
        "ids": [prefix], 
        "name": "Davis Weather Station", 
        "mf": "Davis"
    }
    if unit_of_measure:
        config_payload["unit_of_meas"] = unit_of_measure
    if device_class:
        config_payload["dev_cla"] = device_class
    if entity_category:
        config_payload["ent_cat"] = entity_category
    if state_class:
        config_payload["stat_cla"] = state_class
    if icon:
        config_payload['ic'] = icon
    if MAPPING[key].get('availability', True):
        config_payload['avty_t'] = availability_topic
    client.publish(f"{config_payload['~']}/config", json.dumps(config_payload), retain=True)
    logger.info(f"Sent config for sensor {config_payload['~']}")

def send_data_to_mqtt(client: Any, data: dict[str, Any]):
    for key, value in data.items():
        if not key in MAPPING:
            continue
        if 'has_correct_value' in MAPPING[key]:
            if not MAPPING[key]['has_correct_value'](value):
                continue
        component = MAPPING[key].get('component', 'sensor')
        if 'correction' in MAPPING[key]:
            value = MAPPING[key]['correction'](value)
        if metric_system and 'conversion' in MAPPING[key]:
            conversion = MAPPING[key]['conversion']
            if type(conversion) is dict:
                if alt_windspeed_uom and 'alt' in conversion:
                    conversion = conversion['alt']
                else:
                    conversion = conversion['default']
            value = conversion(value)
        logger.debug(f"{key}={value} (type={type(value)})")
        client.publish(f"{discovery_prefix}/{component}/{prefix}/{MAPPING[key]['topic']}/state", value, retain=True)

def send_last_error_to_mqtt(client: Any, value: str):
    component = MAPPING['LastError'].get('component', 'sensor')
    client.publish(f"{discovery_prefix}/{component}/{prefix}/{MAPPING['LastError']['topic']}/state", value, retain=True)

def add_additional_info(data: dict[str, Any]) -> None:
    data['HeatIndex'] = calc_heat_index(data['TempOut'], data['HumOut'])
    data['WindChill'] = calc_wind_chill(data['TempOut'], data['WindSpeed'])
    data['FeelsLike'] = calc_feels_like(data['TempOut'], data['HumOut'], data['WindSpeed'])
    data['WindDirRose'] = get_wind_rose(data['WindDir'])
    data['DewPoint'] = calc_dew_point(data['TempOut'], data['HumOut'])
    data['WindSpeedBft'] = convert_kmh_to_bft(convert_to_kmh(data['WindSpeed10Min']))
    data['IsRaining'] = "ON" if data['RainRate'] > 0 else "OFF"

def correct_temperature(data: dict[str, Any]):
    if 'TempOut' in data:
        data['TempOut'] -= 0.9
#
# MAIN
#
client = mqtt.Client()
if mqtt_user and mqtt_pass:
    logger.debug('Added MQTT user and password')
    client.username_pw_set(mqtt_user, mqtt_pass)
logger.info("Connecting to MQTT broker")
client.will_set(availability_topic, "offline", 0, True)
client.connect(broker, port)
client.loop_start()

if device:
    link = f'serial:{device}:19200:8N1'
else:
    link = f'tcp:{address}'

logger.info("Connecting to weather station")
vantagepro2 = VantagePro2.from_url(link)
logger.info('Set weather station time to system time')
vantagepro2.settime(datetime.now())

client.publish(availability_topic, "online", 0, True)

while True:
    data: dict[str, Any]
    try:
        vantagepro2.link.open()
        logger.info(f"Acquiring data from {link} using vproweather")
        data = vantagepro2.get_current_data()
    except Exception:
        logger.warning(f"Couldn't acquire data from {link}")
    finally:
        vantagepro2.link.close()

    if data:
        if new_sensor_used:
            correct_temperature(data)
        add_additional_info(data)

        if not hass_configured:
            logger.info('Initializing sensors from Home Assistant to auto discover')
            send_config_to_mqtt(client, data)
            hass_configured = True

        send_data_to_mqtt(client, data)
        logger.info('Data sent to MQTT')
        send_last_error_to_mqtt(client, 'No error')
    else:
        send_last_error_to_mqtt(client, 'Couldn''t acquire data')

    logger.info(f'Now waiting for {interval} seconds for next cycle')
    time.sleep(interval)
